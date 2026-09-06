"""Loop de batalha. Antes cada turno era resolvido chamando a função de batalha
de novo recursivamente (e ela nunca "retornava" de verdade) — aqui é um `while`
comum, então o jogo não acumula profundidade de recursão a cada turno.

Suporta 1 monstro OU um grupo (2-3) — quem chama decide passando um único
MonstroBase ou uma lista deles; o retorno acompanha o formato de entrada
(lista entra, lista sai), então todo código/teste que já lutava contra um
monstro só continua funcionando sem mudar nada.
"""

import random
import string
import time

from ..config import (ATORDOAMENTO_GANHO_POR_ACERTO_FRACO, ATORDOAMENTO_LIMIAR,
                       BONUS_CANALIZACAO_MAXIMO_PERCENTUAL, BONUS_ETEN_PERCENTUAL,
                       BONUS_POSTURA_DEFENSIVA_DANO, BONUS_POSTURA_DEFENSIVA_REDUCAO,
                       BONUS_POSTURA_OFENSIVA_DANO, BONUS_POSTURA_OFENSIVA_DANO_RECEBIDO,
                       CHANCE_APLICAR_EFEITO_STATUS, CHANCE_CRITICO_BASE, CHANCE_CRITICO_MAXIMA,
                       CICLO_ELEMENTAL, FOCO_ARQUEIRO_MAXIMO, FOCO_GANHO_POR_ATAQUE,
                       FOCO_GANHO_POR_CRITICO_EXTRA, FOME_CRITICA, Cor, FURIA_CAVALEIRO_MAXIMA,
                       FURIA_GANHA_AO_ATACAR, FURIA_GANHA_AO_LEVAR_DANO, LIMITE_DEBUFF_PERCENTUAL,
                       MULTIPLICADOR_CRITICO, MULTIPLICADOR_ELITE_ATAQUE,
                       MULTIPLICADOR_FASE_FURIOSA_ATAQUE, MULTIPLICADOR_FRAQUEZA_CICLO,
                       MULTIPLICADOR_FRAQUEZA_ELEMENTAL, MULTIPLICADOR_RESISTENCIA_CICLO,
                       MULTIPLICADOR_RESISTENCIA_ELEMENTAL, PODER_DANO_PERCENTUAL_POR_PONTO,
                       RESSONANCIA_ARCANA_BONUS_POR_STACK, RESSONANCIA_ARCANA_MAXIMA,
                       SIMBOLOS_MINIGAME_CANALIZACAO)
from ..dados.especializacoes import ESPECIALIZACOES
from ..dados.habilidades import HABILIDADES
from ..dados.racas import RACAS
from ..entrada import aguardar_leitura, menu as menu_padrao
from ..interface import barra, limpar_tela
from ..modelos.monstro import MonstroBatalha
from . import efeitos, equipamento, inventario


class ResultadoBatalha:
  VITORIA = 'vitoria'
  DERROTA = 'derrota'
  FUGA = 'fuga'
  MONSTRO_FUGIU = 'monstro_fugiu'


def _ativos(monstros):
  return [m for m in monstros if m.vivo and not m.fugiu]


def multiplicador_elemental(elemento_ataque, monstro):
  if elemento_ataque in monstro.base.fraquezas:
    return MULTIPLICADOR_FRAQUEZA_ELEMENTAL
  if elemento_ataque in monstro.base.resistencias:
    return MULTIPLICADOR_RESISTENCIA_ELEMENTAL
  # Sem fraqueza/resistência explícita: cai pra roda elemental genérica, uma
  # relação mais sutil entre o elemento do ataque e o elemento do monstro.
  if elemento_ataque in CICLO_ELEMENTAL and monstro.base.elemento in CICLO_ELEMENTAL:
    indice_ataque = CICLO_ELEMENTAL.index(elemento_ataque)
    indice_monstro = CICLO_ELEMENTAL.index(monstro.base.elemento)
    tamanho = len(CICLO_ELEMENTAL)
    if (indice_ataque + 1) % tamanho == indice_monstro:
      return MULTIPLICADOR_FRAQUEZA_CICLO
    if (indice_monstro + 1) % tamanho == indice_ataque:
      return MULTIPLICADOR_RESISTENCIA_CICLO
  return 1.0


def _elemento_efetivo(personagem, habilidade):
  """O Arqueiro pode trocar de graça o elemento da flecha em batalha — só
  vale pras habilidades "genéricas" (elemento Fisico); uma habilidade com
  elemento próprio continua com o elemento dela."""
  if personagem.classe == 'Arqueiro' and habilidade.elemento == 'Fisico':
    return personagem.elemento_flecha_atual
  return habilidade.elemento


def chance_de_critico_base(personagem):
  """Chance de crítico sem o bônus específico de uma habilidade — usada na
  tela de Status pra mostrar um número de "vitrine", já que fora de batalha
  não existe uma habilidade selecionada."""
  chance = (CHANCE_CRITICO_BASE + personagem.sorte + personagem.bonus_critico_batalha
            + equipamento.chance_critico_extra_acessorio(personagem))
  especializacao = ESPECIALIZACOES.get(personagem.especializacao)
  if especializacao and especializacao.bonus_tipo == 'critico':
    chance += especializacao.bonus_valor
  return chance


def chance_de_critico(personagem, habilidade):
  return min(CHANCE_CRITICO_MAXIMA, chance_de_critico_base(personagem) + habilidade.bonus_critico)


def _dano_sem_elemento(personagem, habilidade, monstro):
  """Dano determinístico e sem multiplicador elemental (esse é aplicado por
  fora, pra dar pra zerar resistência em habilidades com `ignora_resistencia`).

  Todo bônus percentual (Poder, arma, poção, Etén, raça, fome crítica,
  postura, canalização, ressonância) é somado num total só e aplicado de uma
  vez sobre o dano base. Antes cada bônus multiplicava o resultado do
  anterior (`dano += dano * x/100` em sequência), o que fazia stacks de
  bônus explodirem bem além do esperado.
  """
  bonus_percentual = personagem.poder * PODER_DANO_PERCENTUAL_POR_PONTO
  bonus_percentual += equipamento.bonus_poder_arma_efetivo(personagem)
  if personagem.bonus_dano_batalha:
    bonus_percentual += personagem.bonus_dano_batalha
  if personagem.bonus_canalizacao_pendente:
    bonus_percentual += personagem.bonus_canalizacao_pendente

  debuff = efeitos.bonus_debuff_poder(personagem.efeitos_ativos)
  if debuff:
    bonus_percentual -= debuff

  if personagem.eten:
    bonus_percentual += BONUS_ETEN_PERCENTUAL

  if personagem.fome <= FOME_CRITICA:
    bonus_percentual -= 10

  if personagem.postura == 'ofensiva':
    bonus_percentual += BONUS_POSTURA_OFENSIVA_DANO
  elif personagem.postura == 'defensiva':
    bonus_percentual += BONUS_POSTURA_DEFENSIVA_DANO

  raca = RACAS.get(personagem.raca)
  if raca and raca.bonus_tipo == 'poder':
    bonus_percentual += raca.valor

  especializacao = ESPECIALIZACOES.get(personagem.especializacao)
  elemento_efetivo = _elemento_efetivo(personagem, habilidade)
  if especializacao:
    if especializacao.bonus_tipo == 'dano_elemento' and elemento_efetivo == especializacao.bonus_elemento:
      bonus_percentual += especializacao.bonus_valor
    elif (especializacao.bonus_tipo == 'dano_vida_baixa'
          and personagem.vida <= equipamento.vida_maxima_efetiva(personagem) * 0.5):
      bonus_percentual += especializacao.bonus_valor

  if personagem.classe == 'Mago':
    bonus_percentual += personagem.ressonancia_arcana * RESSONANCIA_ARCANA_BONUS_POR_STACK

  bonus_percentual += efeitos.bonus_vulnerabilidade(monstro.efeitos_ativos)
  bonus_percentual += efeitos.bonus_marcado(monstro.efeitos_ativos)

  bonus_percentual = max(-LIMITE_DEBUFF_PERCENTUAL, bonus_percentual)
  return habilidade.dano_base * (1 + bonus_percentual / 100)


def _multiplicador_elemental_efetivo(personagem, habilidade, monstro):
  elemento = _elemento_efetivo(personagem, habilidade)
  multiplicador = multiplicador_elemental(elemento, monstro)
  if habilidade.ignora_resistencia and multiplicador < 1.0:
    return 1.0
  return multiplicador


def calcular_dano(personagem, habilidade, monstro):
  dano = _dano_sem_elemento(personagem, habilidade, monstro)
  dano *= _multiplicador_elemental_efetivo(personagem, habilidade, monstro)
  critico = habilidade.sempre_critico or random.randint(1, 100) <= chance_de_critico(personagem, habilidade)
  if critico:
    dano *= MULTIPLICADOR_CRITICO
  return max(1, round(dano)), critico


def prever_dano(personagem, habilidade, monstro):
  """Estimativa sem crítico, só para exibir no menu de batalha."""
  dano = _dano_sem_elemento(personagem, habilidade, monstro)
  dano *= _multiplicador_elemental_efetivo(personagem, habilidade, monstro)
  return max(1, round(dano))


def _efeito_grudou(bonus_resistencia=0):
  """Chance compartilhada de um efeito de status (habilidade, ataque de
  monstro, ou acessório) realmente aplicar — antes era garantido em quem
  ataca e só o monstro tinha uma rolagem, o que era injusto pro jogador.
  `bonus_resistencia` (acessório de resistência a efeito) só se aplica a
  efeitos que um MONSTRO tenta grudar no personagem, nunca o contrário."""
  chance = max(0, CHANCE_APLICAR_EFEITO_STATUS - bonus_resistencia)
  return random.randint(1, 100) <= chance


_VALORES_PADRAO_EFEITO = {'Fraqueza': 15, 'Vulnerabilidade': 20, 'Marcado': 25}


def _tentar_detonar_efeito(personagem, monstro, habilidade, escrever):
  """Combo: um ataque Físico (ou uma flecha de Arqueiro trocada pra Físico)
  detona qualquer dano-por-turno ativo no monstro (Queimadura/Sangramento/
  Veneno), causando de uma vez o dano que faltava."""
  if _elemento_efetivo(personagem, habilidade) != 'Fisico':
    return 0
  for efeito_ativo in list(monstro.efeitos_ativos):
    if efeito_ativo['nome'] in efeitos.DANO_POR_TURNO and efeito_ativo['turnos'] > 0:
      bonus = efeitos.DANO_POR_TURNO[efeito_ativo['nome']] * efeito_ativo['turnos']
      monstro.efeitos_ativos.remove(efeito_ativo)
      escrever(f'{Cor.AMARELO}Você detona {efeito_ativo["nome"]} em {monstro.nome}, '
               f'causando {bonus} de dano extra!{Cor.RESET}')
      return bonus
  return 0


def _ganhar_recursos_pos_ataque(personagem, critico):
  """Fúria (Cavaleiro) e Foco (Arqueiro) — ganhos por golpe desferido, sejam
  quantos alvos forem (uma habilidade em área contra 3 monstros rende mais
  recurso que uma contra 1, de propósito)."""
  bonus_extra = equipamento.furia_extra_acessorio(personagem)
  if personagem.classe == 'Cavaleiro':
    personagem.furia_cavaleiro = min(FURIA_CAVALEIRO_MAXIMA,
                                      personagem.furia_cavaleiro + FURIA_GANHA_AO_ATACAR + bonus_extra)
  elif personagem.classe == 'Arqueiro':
    ganho = FOCO_GANHO_POR_ATAQUE + (FOCO_GANHO_POR_CRITICO_EXTRA if critico else 0) + bonus_extra
    personagem.foco_arqueiro = min(FOCO_ARQUEIRO_MAXIMO, personagem.foco_arqueiro + ganho)


def _tentar_contra_ataque(personagem, monstro, escrever):
  """Acessório de contra-ataque: chance de revidar com um golpe simples ao
  esquivar de um ataque de monstro."""
  chance = equipamento.contra_ataque_acessorio(personagem)
  if chance and monstro.vivo and random.randint(1, 100) <= chance:
    dano = max(1, round(personagem.poder * 2 + 10))
    monstro.receber_dano(dano)
    escrever(f'{Cor.AMARELO}Você contra-ataca, causando {dano} de dano em {monstro.nome}!{Cor.RESET}')


def _verificar_atordoamento(monstro, foi_fraqueza, escrever):
  if not foi_fraqueza or not monstro.vivo:
    return
  monstro.stagger += ATORDOAMENTO_GANHO_POR_ACERTO_FRACO
  if monstro.stagger >= ATORDOAMENTO_LIMIAR:
    monstro.stagger = 0
    efeitos.aplicar_efeito(monstro.efeitos_ativos, 'Atordoado', 1)
    escrever(f'{Cor.AMARELO}{monstro.nome} está atordoado pelo acúmulo de golpes na fraqueza!{Cor.RESET}')


def _verificar_fase_furiosa(monstro, escrever):
  if not monstro.base.tem_fase_furiosa or monstro.fase_furiosa_ativa or not monstro.vivo:
    return
  if monstro.vida <= monstro.vida_maxima_real * 0.5:
    monstro.fase_furiosa_ativa = True
    escrever(f'{Cor.VERMELHO}{monstro.nome} entra em fúria — fica mais perigoso pro resto da luta!{Cor.RESET}')


def personagem_ataca(personagem, habilidade, monstro, escrever):
  """Ataque contra um único alvo — usada tanto em lutas solo quanto, alvo a
  alvo, por `personagem_ataca_alvos` quando há um grupo."""
  nome_colorido = f'{Cor.BRANCO}{habilidade.nome}{Cor.RESET}'
  foi_fraqueza = _multiplicador_elemental_efetivo(personagem, habilidade, monstro) > 1.0
  if habilidade.tipo == 'ataque_multiplo':
    acertos = random.randint(habilidade.acertos_min, habilidade.acertos_max)
    dano_por_acerto, critico = calcular_dano(personagem, habilidade, monstro)
    dano_total = dano_por_acerto * acertos
    monstro.receber_dano(dano_total)
    sufixo = f' {Cor.AMARELO}(CRÍTICO!){Cor.RESET}' if critico else ''
    escrever(f'Você usa {nome_colorido} e acerta {acertos}x, causando '
             f'{Cor.VERMELHO}{dano_total} de dano{Cor.RESET} no {monstro.nome}{sufixo}.')
  else:
    dano, critico = calcular_dano(personagem, habilidade, monstro)
    monstro.receber_dano(dano)
    sufixo = f' {Cor.AMARELO}(CRÍTICO!){Cor.RESET}' if critico else ''
    escrever(f'Você usa {nome_colorido}, causando '
             f'{Cor.VERMELHO}{dano} de dano{Cor.RESET} no {monstro.nome}{sufixo}.')

  personagem.bonus_canalizacao_pendente = 0

  bonus_detonacao = _tentar_detonar_efeito(personagem, monstro, habilidade, escrever)
  if bonus_detonacao:
    monstro.receber_dano(bonus_detonacao)

  _verificar_atordoamento(monstro, foi_fraqueza, escrever)
  _verificar_fase_furiosa(monstro, escrever)

  if not monstro.vivo:
    bonus_vida_ao_matar = equipamento.vida_ao_matar_acessorio(personagem)
    if bonus_vida_ao_matar:
      vida_max = equipamento.vida_maxima_efetiva(personagem)
      cura = round(vida_max * bonus_vida_ao_matar / 100)
      personagem.vida = min(vida_max, personagem.vida + cura)
      escrever(f'{Cor.VERDE}Seu acessório recupera {cura} de vida por acabar com {monstro.nome}!{Cor.RESET}')

  if habilidade.efeito and monstro.vivo:
    if _efeito_grudou():
      valor = _VALORES_PADRAO_EFEITO.get(habilidade.efeito, 0)
      efeitos.aplicar_efeito(monstro.efeitos_ativos, habilidade.efeito, habilidade.turnos_efeito, valor)
      escrever(f'{Cor.VERMELHO}O {monstro.nome} sofreu {habilidade.efeito}!{Cor.RESET}')
    else:
      escrever(f'{Cor.CINZA}O {monstro.nome} resistiu ao {habilidade.efeito}.{Cor.RESET}')

  if habilidade.cura_percentual_usuario:
    vida_max = equipamento.vida_maxima_efetiva(personagem)
    cura = round(vida_max * habilidade.cura_percentual_usuario / 100)
    personagem.vida = min(vida_max, personagem.vida + cura)
    escrever(f'{Cor.VERDE}Você se cura em {cura} de vida!{Cor.RESET}')

  if habilidade.efeito_no_usuario:
    efeitos.aplicar_efeito(personagem.efeitos_ativos, habilidade.efeito_no_usuario,
                            habilidade.turnos_efeito_no_usuario)
    escrever(f'{Cor.VERDE}Você ganhou {habilidade.efeito_no_usuario}!{Cor.RESET}')

  _ganhar_recursos_pos_ataque(personagem, critico)


def personagem_ataca_alvos(personagem, habilidade, alvos, escrever):
  """Resolve um ataque contra 1+ alvos — usada quando a batalha tem mais de
  um monstro (grupo). Habilidade em área acerta todos de cheio; as demais
  (incl. ataque_multiplo) miram só o primeiro alvo vivo da lista recebida —
  a escolha de QUAL vira "o primeiro" já é feita antes, em `batalhar`."""
  vivos = [a for a in alvos if a.vivo]
  if not vivos:
    return
  if habilidade.tipo == 'ataque_area':
    for alvo in list(vivos):
      if alvo.vivo:
        personagem_ataca(personagem, habilidade, alvo, escrever)
    return
  personagem_ataca(personagem, habilidade, vivos[0], escrever)


def _atualizar_ressonancia_arcana(personagem, habilidade):
  if personagem.classe != 'Mago' or habilidade.elemento == 'Fisico':
    return
  elemento_efetivo = _elemento_efetivo(personagem, habilidade)
  if elemento_efetivo == personagem.ultimo_elemento_conjurado:
    personagem.ressonancia_arcana = 0
  else:
    personagem.ressonancia_arcana = min(RESSONANCIA_ARCANA_MAXIMA, personagem.ressonancia_arcana + 1)
  personagem.ultimo_elemento_conjurado = elemento_efetivo


def _receber_ataque_do_monstro(personagem, dano_bruto, descricao, escrever):
  bonus_percentual = 0
  if personagem.postura == 'ofensiva':
    bonus_percentual += BONUS_POSTURA_OFENSIVA_DANO_RECEBIDO
  elif personagem.postura == 'defensiva':
    bonus_percentual -= BONUS_POSTURA_DEFENSIVA_REDUCAO
  bonus_percentual -= equipamento.reducao_dano_acessorio(personagem)

  dano = dano_bruto
  if bonus_percentual:
    dano = max(1, round(dano + dano * bonus_percentual / 100))

  personagem.vida = max(0, personagem.vida - dano)
  escrever(f'{descricao}, causando {Cor.VERMELHO}{dano} de dano{Cor.RESET} em você.')

  if personagem.classe == 'Cavaleiro':
    personagem.furia_cavaleiro = min(FURIA_CAVALEIRO_MAXIMA,
                                      personagem.furia_cavaleiro + FURIA_GANHA_AO_LEVAR_DANO)


def monstro_ataca(personagem, monstro, escrever):
  """Devolve True se o monstro fugiu da batalha."""
  if efeitos.verificar_paralisia(monstro.efeitos_ativos, escrever, monstro.nome):
    return False

  if monstro.base.tem_investida_especial:
    if monstro.carregando_investida:
      monstro.carregando_investida = False
      dano = round(random.randint(monstro.base.ataque_min, monstro.base.ataque_max) * 2)
      if monstro.elite:
        dano = round(dano * MULTIPLICADOR_ELITE_ATAQUE)
      if monstro.fase_furiosa_ativa:
        dano = round(dano * MULTIPLICADOR_FASE_FURIOSA_ATAQUE)
      esquiva = personagem.esquiva + personagem.bonus_esquiva_batalha + equipamento.esquiva_flat_acessorio(personagem)
      if random.randint(1, 100) <= esquiva:
        escrever(f'{Cor.AMARELO}Você esquiva da investida especial de {monstro.nome}!{Cor.RESET}')
        _tentar_contra_ataque(personagem, monstro, escrever)
        return False
      _receber_ataque_do_monstro(
          personagem, dano, f'{Cor.VERMELHO}{monstro.nome} desfere seu golpe especial!{Cor.RESET}', escrever)
      return False
    if random.randint(1, 4) == 1:
      monstro.carregando_investida = True
      escrever(f'{Cor.AMARELO}{monstro.nome} está se preparando para um golpe poderoso!{Cor.RESET}')
      return False

  if monstro.base.foge_com_pouca_vida and not monstro.tentou_fugir:
    if monstro.vida <= monstro.vida_maxima_real * 0.2:
      monstro.tentou_fugir = True
      if random.randint(1, 2) == 1:
        escrever(f'{Cor.AMARELO}{monstro.nome} foge apavorado da batalha!{Cor.RESET}')
        return True

  esquiva = personagem.esquiva + personagem.bonus_esquiva_batalha + equipamento.esquiva_flat_acessorio(personagem)
  if random.randint(1, 100) <= esquiva:
    escrever(f'{Cor.AMARELO}Você esquiva do ataque do monstro!{Cor.RESET}')
    _tentar_contra_ataque(personagem, monstro, escrever)
    return False

  dano = random.randint(monstro.base.ataque_min, monstro.base.ataque_max)
  if monstro.elite:
    dano = round(dano * MULTIPLICADOR_ELITE_ATAQUE)
  if monstro.fase_furiosa_ativa:
    dano = round(dano * MULTIPLICADOR_FASE_FURIOSA_ATAQUE)

  debuff = efeitos.bonus_debuff_poder(monstro.efeitos_ativos)
  if debuff:
    dano = max(1, round(dano - dano * debuff / 100))

  descricao = random.choice(monstro.base.descricoes_ataque)
  _receber_ataque_do_monstro(personagem, dano, descricao, escrever)

  if monstro.base.efeito_aplicado:
    resistencia = equipamento.resistencia_efeito_acessorio(personagem)
    if _efeito_grudou(resistencia):
      efeitos.aplicar_efeito(personagem.efeitos_ativos, monstro.base.efeito_aplicado,
                              monstro.base.turnos_efeito_aplicado)
      escrever(f'{Cor.VERMELHO}Você sofreu {monstro.base.efeito_aplicado}!{Cor.RESET}')
    else:
      escrever(f'{Cor.CINZA}Você resistiu ao {monstro.base.efeito_aplicado}.{Cor.RESET}')

  return False


def _tela_batalha(personagem, monstros):
  vida_max = equipamento.vida_maxima_efetiva(personagem)
  mana_max = equipamento.mana_maxima_efetiva(personagem)
  linhas_monstros = []
  for m in _ativos(monstros):
    linhas_monstros.append(f'  {m.nome}: {barra(m.vida, m.vida_maxima_real, cor=Cor.VERMELHO)}')
  titulo = (f'  {Cor.BRANCO}Batalha{Cor.RESET}\n' + '\n'.join(linhas_monstros) + '\n\n'
            f'  Sua vida: {barra(personagem.vida, vida_max, cor=Cor.VERMELHO)}\n'
            f'  Sua mana: {barra(personagem.mana, mana_max, cor=Cor.AZUL)}\n'
            f'  Postura: {personagem.postura}')
  if personagem.classe == 'Cavaleiro':
    titulo += f'   Fúria: {personagem.furia_cavaleiro}/{FURIA_CAVALEIRO_MAXIMA}'
  elif personagem.classe == 'Arqueiro':
    titulo += (f'   Foco: {personagem.foco_arqueiro}/{FOCO_ARQUEIRO_MAXIMO}'
               f'   Flecha: {personagem.elemento_flecha_atual}')
  elif personagem.classe == 'Mago':
    titulo += f'   Ressonância Arcana: {personagem.ressonancia_arcana}/{RESSONANCIA_ARCANA_MAXIMA}'
  return titulo


def _descricao_habilidade(personagem, habilidade, monstro):
  cd = personagem.cooldowns.get(habilidade.nome, 0)
  estado = f'{Cor.VERMELHO}[Cooldown: {cd}]{Cor.RESET}' if cd > 0 else f'{Cor.VERDE}Pronta{Cor.RESET}'
  dano_previsto = prever_dano(personagem, habilidade, monstro)
  efeito = f' | Efeito: {habilidade.efeito} ({habilidade.turnos_efeito}t)' if habilidade.efeito else ''
  if habilidade.custo_furia:
    custo = f'{habilidade.custo_furia} Fúria'
  elif habilidade.custo_foco:
    custo = f'{habilidade.custo_foco} Foco'
  else:
    custo = f'{habilidade.mana} mana'
  canal = f' {Cor.CIANO}[Canalizável]{Cor.RESET}' if habilidade.canalizavel else ''
  return (f'{Cor.BRANCO}{habilidade.nome}{Cor.RESET} — '
          f'{Cor.AZUL}{custo}{Cor.RESET}, '
          f'{Cor.VERMELHO}~{dano_previsto} dano{Cor.RESET} '
          f'({_elemento_efetivo(personagem, habilidade)}){efeito}{canal} — {estado}')


def _abrir_itens_de_batalha(personagem, escrever, ler_acao):
  """Devolve True se um item foi de fato consumido."""
  opcoes_pocao = [nome for nome, qtd in personagem.pocoes.items() if qtd > 0]
  if not opcoes_pocao:
    escrever(f'{Cor.VERMELHO}Você não tem poções.{Cor.RESET}')
    return False
  escolha = ler_acao('Qual poção usar?', opcoes_pocao)
  if escolha is None:
    return False
  return inventario.usar_pocao(personagem, opcoes_pocao[escolha], em_batalha=True, escrever=escrever)


def _minigame_canalizacao(escrever, limpar, esperar, entrada_texto):
  """Mini-jogo de memória: memoriza a sequência e digita de volta — quanto
  mais acertar, maior o bônus no próximo golpe. Mesmo molde do desafio do
  Mestre de Habusken, só que dentro da batalha."""
  simbolos = [random.choice(string.ascii_uppercase) for _ in range(SIMBOLOS_MINIGAME_CANALIZACAO)]
  limpar()
  escrever(f'{Cor.BRANCO}Canalizando... memorize a sequência:{Cor.RESET}')
  for simbolo in simbolos:
    escrever(f'{Cor.AMARELO}{simbolo}{Cor.RESET}')
    esperar(0.6)
  esperar(1)
  limpar()
  resposta = entrada_texto('Digite a sequência, sem espaços (ex: ABCD): -->').strip().upper()
  acertos = sum(1 for certo, digitado in zip(simbolos, resposta) if certo == digitado)
  return acertos, len(simbolos)


def batalhar(personagem, monstro_base, escrever=None, ler_acao=None, aguardar=None, elite=False,
             limpar=None, esperar=None, entrada_texto=None):
  """Roda uma batalha inteira e devolve (ResultadoBatalha.*, monstro_ou_lista).

  `monstro_base` pode ser um único MonstroBase (luta solo — devolve um único
  MonstroBatalha, como sempre) ou uma lista deles (grupo — devolve a lista).
  """
  escrever = escrever or print
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  limpar = limpar or limpar_tela
  esperar = esperar or time.sleep
  entrada_texto = entrada_texto or input

  eh_grupo = isinstance(monstro_base, (list, tuple))
  bases = list(monstro_base) if eh_grupo else [monstro_base]
  monstros = [MonstroBatalha.instanciar(mb, elite=elite) for mb in bases]

  def _devolver(resultado):
    return resultado, (monstros if eh_grupo else monstros[0])

  personagem.local = 'batalha'
  personagem.bonus_dano_batalha = 0
  personagem.bonus_esquiva_batalha = 0
  personagem.bonus_critico_batalha = 0
  personagem.bonus_canalizacao_pendente = 0
  personagem.item_usado_neste_turno = False
  personagem.pocao_poder_usada = False
  personagem.pocao_esquiva_usada = False
  personagem.pocao_furia_usada = False
  for nome_habilidade in personagem.habilidades_equipadas:
    personagem.cooldowns[nome_habilidade] = 0

  for monstro in monstros:
    for nome_efeito, turnos in equipamento.efeitos_iniciais_de_batalha_acessorios(personagem):
      if _efeito_grudou():
        efeitos.aplicar_efeito(monstro.efeitos_ativos, nome_efeito, turnos)
        escrever(f'{Cor.VERMELHO}Seu acessório inflige {nome_efeito} no {monstro.nome} '
                 f'assim que a batalha começa!{Cor.RESET}')

  sufixo_elite = f' {Cor.AMARELO}(ELITE){Cor.RESET}' if elite else ''
  if eh_grupo:
    nomes = ', '.join(m.nome for m in monstros)
    escrever(f'{Cor.BRANCO}Você entrou em batalha contra um grupo: {nomes}!{Cor.RESET}')
  else:
    escrever(f'{Cor.BRANCO}Você entrou em batalha contra {monstros[0].nome}!{Cor.RESET}{sufixo_elite}')
  aguardar()

  while True:
    if personagem.vida <= 0:
      return _devolver(ResultadoBatalha.DERROTA)
    if not _ativos(monstros):
      return _devolver(ResultadoBatalha.VITORIA)

    vida_maxima_efetiva = equipamento.vida_maxima_efetiva(personagem)
    personagem.vida = efeitos.processar_efeitos_continuos(
        personagem.efeitos_ativos, personagem.vida, escrever, 'Você', vida_maxima=vida_maxima_efetiva)

    bonus_regen_acessorio = equipamento.regeneracao_acessorio(personagem)
    if bonus_regen_acessorio and 0 < personagem.vida < vida_maxima_efetiva:
      cura = round(vida_maxima_efetiva * bonus_regen_acessorio / 100)
      if cura:
        personagem.vida = min(vida_maxima_efetiva, personagem.vida + cura)
        escrever(f'{Cor.VERDE}Seu acessório regenera {cura} de vida.{Cor.RESET}')

    if personagem.vida <= 0:
      aguardar()
      return _devolver(ResultadoBatalha.DERROTA)

    habilidades_ativas = [HABILIDADES[nome] for nome in personagem.habilidades_equipadas]

    # Fase de escolha: repete em caso de escolha inválida, sem passar a vez.
    while True:
      alvo_referencia = _ativos(monstros)[0]
      labels = [_descricao_habilidade(personagem, h, alvo_referencia) for h in habilidades_ativas]
      acoes = ['habilidade'] * len(habilidades_ativas)

      proxima_postura = 'defensiva' if personagem.postura == 'ofensiva' else 'ofensiva'
      labels.append(f'Mudar postura para {proxima_postura} (atual: {personagem.postura})')
      acoes.append('postura')

      if personagem.classe == 'Arqueiro':
        indice_atual = CICLO_ELEMENTAL.index(personagem.elemento_flecha_atual)
        proximo_elemento = CICLO_ELEMENTAL[(indice_atual + 1) % len(CICLO_ELEMENTAL)]
        labels.append(f'Trocar flecha para {proximo_elemento} (atual: {personagem.elemento_flecha_atual})')
        acoes.append('trocar_elemento')

      labels += ['Itens', 'Pular a vez', 'Tentar fugir']
      acoes += ['itens', 'pular', 'fugir']

      escolha = ler_acao(_tela_batalha(personagem, monstros), labels, com_voltar=False)
      tipo_acao = acoes[escolha]

      if tipo_acao == 'habilidade':
        habilidade = habilidades_ativas[escolha]
        if personagem.cooldowns.get(habilidade.nome, 0) > 0:
          escrever(f'{Cor.VERMELHO}Essa habilidade ainda está em cooldown.{Cor.RESET}')
          aguardar()
          continue
        if habilidade.custo_furia > 0:
          if personagem.furia_cavaleiro < habilidade.custo_furia:
            escrever(f'{Cor.VERMELHO}Fúria insuficiente.{Cor.RESET}')
            aguardar()
            continue
          personagem.furia_cavaleiro -= habilidade.custo_furia
        elif habilidade.custo_foco > 0:
          if personagem.foco_arqueiro < habilidade.custo_foco:
            escrever(f'{Cor.VERMELHO}Foco insuficiente.{Cor.RESET}')
            aguardar()
            continue
          personagem.foco_arqueiro -= habilidade.custo_foco
        else:
          if personagem.mana < habilidade.mana:
            escrever(f'{Cor.VERMELHO}Mana insuficiente.{Cor.RESET}')
            aguardar()
            continue
          personagem.mana -= habilidade.mana

        ativos_agora = _ativos(monstros)
        if len(ativos_agora) > 1 and habilidade.tipo != 'ataque_area':
          escolha_alvo = ler_acao('Escolha o alvo:', [m.nome for m in ativos_agora])
          if escolha_alvo is None:
            # devolve o recurso já descontado, já que a ação foi cancelada
            if habilidade.custo_furia > 0:
              personagem.furia_cavaleiro = min(FURIA_CAVALEIRO_MAXIMA,
                                                personagem.furia_cavaleiro + habilidade.custo_furia)
            elif habilidade.custo_foco > 0:
              personagem.foco_arqueiro = min(FOCO_ARQUEIRO_MAXIMO,
                                              personagem.foco_arqueiro + habilidade.custo_foco)
            else:
              personagem.mana = min(equipamento.mana_maxima_efetiva(personagem),
                                     personagem.mana + habilidade.mana)
            continue
          alvos = [ativos_agora[escolha_alvo]] + [m for m in ativos_agora if m is not ativos_agora[escolha_alvo]]
        else:
          alvos = ativos_agora

        if habilidade.canalizavel:
          quer_canalizar = ler_acao(
              f'Canalizar {habilidade.nome} pra fortalecer com um mini-jogo de memória?',
              ['Sim, canalizar', 'Não, usar normal'])
          if quer_canalizar == 0:
            acertos, total = _minigame_canalizacao(escrever, limpar, esperar, entrada_texto)
            personagem.bonus_canalizacao_pendente = round(BONUS_CANALIZACAO_MAXIMO_PERCENTUAL * acertos / total)
            escrever(f'{Cor.CIANO}Canalização: {acertos}/{total} — '
                     f'+{personagem.bonus_canalizacao_pendente}% de dano no golpe!{Cor.RESET}')

        personagem.cooldowns[habilidade.nome] = habilidade.cooldown_max
        personagem_ataca_alvos(personagem, habilidade, alvos, escrever)
        _atualizar_ressonancia_arcana(personagem, habilidade)
        break

      if tipo_acao == 'postura':
        personagem.postura = proxima_postura
        escrever(f'Você muda para postura {Cor.BRANCO}{proxima_postura}{Cor.RESET}.')
        aguardar()
        continue  # trocar de postura é de graça — não passa a vez pro monstro

      if tipo_acao == 'trocar_elemento':
        personagem.elemento_flecha_atual = proximo_elemento
        escrever(f'Você troca sua flecha para o elemento {Cor.BRANCO}{proximo_elemento}{Cor.RESET}.')
        aguardar()
        continue  # de graça, como a postura

      if tipo_acao == 'itens':
        if personagem.item_usado_neste_turno:
          escrever(f'{Cor.VERMELHO}Você já usou um item nesse turno.{Cor.RESET}')
          aguardar()
          continue
        usou = _abrir_itens_de_batalha(personagem, escrever, ler_acao)
        if usou:
          personagem.item_usado_neste_turno = True
        aguardar()
        continue  # usar item não passa a vez — só não dá pra usar 2 no mesmo turno

      if tipo_acao == 'pular':
        escrever('Você pula a vez.')
      elif tipo_acao == 'fugir':
        if random.randint(1, 5) == 1:
          escrever(f'{Cor.VERDE}Você fugiu com sucesso!{Cor.RESET}')
          aguardar()
          return _devolver(ResultadoBatalha.FUGA)
        escrever(f'{Cor.VERMELHO}Você não conseguiu fugir!{Cor.RESET}')
      break

    mana_max = equipamento.mana_maxima_efetiva(personagem)
    personagem.mana = min(mana_max, personagem.mana + round(mana_max * 0.1))
    personagem.item_usado_neste_turno = False

    if not _ativos(monstros):
      aguardar()
      return _devolver(ResultadoBatalha.VITORIA)

    # Queimadura/Sangramento/Veneno/Regeneração aplicados NOS monstros nunca
    # eram processados — só os efeitos do próprio jogador tinham esse tratamento.
    for monstro in _ativos(monstros):
      monstro.vida = efeitos.processar_efeitos_continuos(
          monstro.efeitos_ativos, monstro.vida, escrever, monstro.nome, vida_maxima=monstro.vida_maxima_real)

    if not _ativos(monstros):
      aguardar()
      return _devolver(ResultadoBatalha.VITORIA)

    for monstro in _ativos(monstros):
      if personagem.vida <= 0:
        break
      fugiu = monstro_ataca(personagem, monstro, escrever)
      aguardar()
      if fugiu:
        monstro.fugiu = True
        if not eh_grupo:
          return _devolver(ResultadoBatalha.MONSTRO_FUGIU)
        escrever(f'{Cor.CIANO}{monstro.nome} fugiu da batalha!{Cor.RESET}')

    if personagem.vida <= 0:
      return _devolver(ResultadoBatalha.DERROTA)

    for nome in personagem.cooldowns:
      if personagem.cooldowns[nome] > 0:
        personagem.cooldowns[nome] -= 1
