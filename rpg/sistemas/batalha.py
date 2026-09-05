"""Loop de batalha. Antes cada turno era resolvido chamando a função de batalha
de novo recursivamente (e ela nunca "retornava" de verdade) — aqui é um `while`
comum, então o jogo não acumula profundidade de recursão a cada turno.
"""

import random

from ..config import (AUTOBATALHA_TURNOS, AUTOBATALHA_VIDA_MINIMA_PERCENTUAL,
                       BONUS_ETEN_PERCENTUAL, BONUS_POSTURA_DEFENSIVA_DANO,
                       BONUS_POSTURA_DEFENSIVA_REDUCAO, BONUS_POSTURA_OFENSIVA_DANO,
                       BONUS_POSTURA_OFENSIVA_DANO_RECEBIDO, CHANCE_APLICAR_EFEITO_STATUS,
                       CHANCE_CRITICO_BASE, CHANCE_CRITICO_MAXIMA, CICLO_ELEMENTAL, FOME_CRITICA,
                       Cor, FURIA_CAVALEIRO_MAXIMA, FURIA_GANHA_AO_ATACAR,
                       FURIA_GANHA_AO_LEVAR_DANO, LIMITE_DEBUFF_PERCENTUAL, MULTIPLICADOR_CRITICO,
                       MULTIPLICADOR_ELITE_ATAQUE, MULTIPLICADOR_FRAQUEZA_CICLO,
                       MULTIPLICADOR_FRAQUEZA_ELEMENTAL, MULTIPLICADOR_RESISTENCIA_CICLO,
                       MULTIPLICADOR_RESISTENCIA_ELEMENTAL, PODER_DANO_PERCENTUAL_POR_PONTO)
from ..dados.especializacoes import ESPECIALIZACOES
from ..dados.habilidades import HABILIDADES
from ..dados.racas import RACAS
from ..entrada import aguardar_leitura, menu as menu_padrao
from ..interface import barra
from ..modelos.monstro import MonstroBatalha
from . import efeitos, equipamento, inventario


class ResultadoBatalha:
  VITORIA = 'vitoria'
  DERROTA = 'derrota'
  FUGA = 'fuga'
  MONSTRO_FUGIU = 'monstro_fugiu'


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
  postura) é somado num total só e aplicado de uma vez sobre o dano base.
  Antes cada bônus multiplicava o resultado do anterior (`dano += dano *
  x/100` em sequência), o que fazia stacks de bônus explodirem bem além do
  esperado — por isso dava pra derrubar monstro de andar muito acima do
  nível real.
  """
  bonus_percentual = personagem.poder * PODER_DANO_PERCENTUAL_POR_PONTO
  bonus_percentual += equipamento.bonus_poder_arma_efetivo(personagem)
  if personagem.bonus_dano_batalha:
    bonus_percentual += personagem.bonus_dano_batalha

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
  if especializacao:
    if especializacao.bonus_tipo == 'dano_elemento' and habilidade.elemento == especializacao.bonus_elemento:
      bonus_percentual += especializacao.bonus_valor
    elif (especializacao.bonus_tipo == 'dano_vida_baixa'
          and personagem.vida <= equipamento.vida_maxima_efetiva(personagem) * 0.5):
      bonus_percentual += especializacao.bonus_valor

  bonus_percentual += efeitos.bonus_vulnerabilidade(monstro.efeitos_ativos)

  bonus_percentual = max(-LIMITE_DEBUFF_PERCENTUAL, bonus_percentual)
  return habilidade.dano_base * (1 + bonus_percentual / 100)


def _multiplicador_elemental_efetivo(habilidade, monstro):
  multiplicador = multiplicador_elemental(habilidade.elemento, monstro)
  if habilidade.ignora_resistencia and multiplicador < 1.0:
    return 1.0
  return multiplicador


def calcular_dano(personagem, habilidade, monstro):
  dano = _dano_sem_elemento(personagem, habilidade, monstro)
  dano *= _multiplicador_elemental_efetivo(habilidade, monstro)
  critico = habilidade.sempre_critico or random.randint(1, 100) <= chance_de_critico(personagem, habilidade)
  if critico:
    dano *= MULTIPLICADOR_CRITICO
  return max(1, round(dano)), critico


def prever_dano(personagem, habilidade, monstro):
  """Estimativa sem crítico, só para exibir no menu de batalha."""
  dano = _dano_sem_elemento(personagem, habilidade, monstro)
  dano *= _multiplicador_elemental_efetivo(habilidade, monstro)
  return max(1, round(dano))


def _efeito_grudou():
  """Chance compartilhada de um efeito de status (habilidade, ataque de
  monstro, ou acessório) realmente aplicar — antes era garantido em quem
  ataca e só o monstro tinha uma rolagem, o que era injusto pro jogador."""
  return random.randint(1, 100) <= CHANCE_APLICAR_EFEITO_STATUS


def _tentar_detonar_efeito(monstro, habilidade, escrever):
  """Combo: um ataque Físico detona qualquer dano-por-turno ativo no monstro
  (Queimadura/Sangramento/Veneno), causando de uma vez o dano que faltava."""
  if habilidade.elemento != 'Fisico':
    return 0
  for efeito_ativo in list(monstro.efeitos_ativos):
    if efeito_ativo['nome'] in efeitos.DANO_POR_TURNO and efeito_ativo['turnos'] > 0:
      bonus = efeitos.DANO_POR_TURNO[efeito_ativo['nome']] * efeito_ativo['turnos']
      monstro.efeitos_ativos.remove(efeito_ativo)
      escrever(f'{Cor.AMARELO}Você detona {efeito_ativo["nome"]} em {monstro.nome}, '
               f'causando {bonus} de dano extra!{Cor.RESET}')
      return bonus
  return 0


def personagem_ataca(personagem, habilidade, monstro, escrever):
  nome_colorido = f'{Cor.BRANCO}{habilidade.nome}{Cor.RESET}'
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

  bonus_detonacao = _tentar_detonar_efeito(monstro, habilidade, escrever)
  if bonus_detonacao:
    monstro.receber_dano(bonus_detonacao)

  if habilidade.efeito and monstro.vivo:
    if _efeito_grudou():
      valor = 15 if habilidade.efeito == 'Fraqueza' else (20 if habilidade.efeito == 'Vulnerabilidade' else 0)
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

  if personagem.classe == 'Cavaleiro':
    personagem.furia_cavaleiro = min(FURIA_CAVALEIRO_MAXIMA,
                                      personagem.furia_cavaleiro + FURIA_GANHA_AO_ATACAR)


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
  """Devolve True se o monstro fugiu da batalha (acaba sem vitória nem derrota)."""
  if efeitos.verificar_paralisia(monstro.efeitos_ativos, escrever, monstro.nome):
    return False

  if monstro.base.tem_investida_especial:
    if monstro.carregando_investida:
      monstro.carregando_investida = False
      dano = round(random.randint(monstro.base.ataque_min, monstro.base.ataque_max) * 2)
      if monstro.elite:
        dano = round(dano * MULTIPLICADOR_ELITE_ATAQUE)
      esquiva = personagem.esquiva + personagem.bonus_esquiva_batalha + equipamento.esquiva_flat_acessorio(personagem)
      if random.randint(1, 100) <= esquiva:
        escrever(f'{Cor.AMARELO}Você esquiva da investida especial de {monstro.nome}!{Cor.RESET}')
        return False
      _receber_ataque_do_monstro(
          personagem, dano, f'{Cor.VERMELHO}{monstro.nome} desfere seu golpe especial!{Cor.RESET}', escrever)
      return False
    if random.randint(1, 4) == 1:
      monstro.carregando_investida = True
      escrever(f'{Cor.AMARELO}{monstro.nome} está se preparando para um golpe poderoso!{Cor.RESET}')
      return False

  if monstro.base.foge_com_pouca_vida and not monstro.tentou_fugir:
    vida_maxima_real = round(monstro.base.vida_maxima * (1.8 if monstro.elite else 1.0))
    if monstro.vida <= vida_maxima_real * 0.2:
      monstro.tentou_fugir = True
      if random.randint(1, 2) == 1:
        escrever(f'{Cor.AMARELO}{monstro.nome} foge apavorado da batalha!{Cor.RESET}')
        return True

  esquiva = personagem.esquiva + personagem.bonus_esquiva_batalha + equipamento.esquiva_flat_acessorio(personagem)
  if random.randint(1, 100) <= esquiva:
    escrever(f'{Cor.AMARELO}Você esquiva do ataque do monstro!{Cor.RESET}')
    return False

  dano = random.randint(monstro.base.ataque_min, monstro.base.ataque_max)
  if monstro.elite:
    dano = round(dano * MULTIPLICADOR_ELITE_ATAQUE)

  debuff = efeitos.bonus_debuff_poder(monstro.efeitos_ativos)
  if debuff:
    dano = max(1, round(dano - dano * debuff / 100))

  descricao = random.choice(monstro.base.descricoes_ataque)
  _receber_ataque_do_monstro(personagem, dano, descricao, escrever)

  if monstro.base.efeito_aplicado:
    if _efeito_grudou():
      efeitos.aplicar_efeito(personagem.efeitos_ativos, monstro.base.efeito_aplicado,
                              monstro.base.turnos_efeito_aplicado)
      escrever(f'{Cor.VERMELHO}Você sofreu {monstro.base.efeito_aplicado}!{Cor.RESET}')
    else:
      escrever(f'{Cor.CINZA}Você resistiu ao {monstro.base.efeito_aplicado}.{Cor.RESET}')

  return False


def _tela_batalha(personagem, monstro):
  vida_max = equipamento.vida_maxima_efetiva(personagem)
  mana_max = equipamento.mana_maxima_efetiva(personagem)
  vida_max_monstro = round(monstro.base.vida_maxima * (1.8 if monstro.elite else 1.0))
  titulo = (f'  {Cor.BRANCO}Batalha contra {monstro.nome}{Cor.RESET}\n'
            f'  Vida do inimigo: {barra(monstro.vida, vida_max_monstro, cor=Cor.VERMELHO)}\n\n'
            f'  Sua vida: {barra(personagem.vida, vida_max, cor=Cor.VERMELHO)}\n'
            f'  Sua mana: {barra(personagem.mana, mana_max, cor=Cor.AZUL)}\n'
            f'  Postura: {personagem.postura}')
  if personagem.classe == 'Cavaleiro':
    titulo += f'   Fúria: {personagem.furia_cavaleiro}/{FURIA_CAVALEIRO_MAXIMA}'
  return titulo


def _descricao_habilidade(personagem, habilidade, monstro):
  cd = personagem.cooldowns.get(habilidade.nome, 0)
  estado = f'{Cor.VERMELHO}[Cooldown: {cd}]{Cor.RESET}' if cd > 0 else f'{Cor.VERDE}Pronta{Cor.RESET}'
  dano_previsto = prever_dano(personagem, habilidade, monstro)
  efeito = f' | Efeito: {habilidade.efeito} ({habilidade.turnos_efeito}t)' if habilidade.efeito else ''
  custo = f'{habilidade.custo_furia} Fúria' if habilidade.custo_furia else f'{habilidade.mana} mana'
  return (f'{Cor.BRANCO}{habilidade.nome}{Cor.RESET} — '
          f'{Cor.AZUL}{custo}{Cor.RESET}, '
          f'{Cor.VERMELHO}~{dano_previsto} dano{Cor.RESET} '
          f'({habilidade.elemento}){efeito} — {estado}')


def _melhor_habilidade_disponivel(personagem, habilidades_ativas, monstro):
  """Habilidade de maior dano previsto entre as que estão fora de cooldown e
  com recurso (mana ou Fúria) suficiente — usada pela autobatalha."""
  candidatas = []
  for habilidade in habilidades_ativas:
    if personagem.cooldowns.get(habilidade.nome, 0) > 0:
      continue
    if habilidade.custo_furia > 0:
      if personagem.furia_cavaleiro < habilidade.custo_furia:
        continue
    elif personagem.mana < habilidade.mana:
      continue
    candidatas.append(habilidade)
  if not candidatas:
    return None
  return max(candidatas, key=lambda h: prever_dano(personagem, h, monstro))


def _abrir_itens_de_batalha(personagem, escrever, ler_acao):
  opcoes_pocao = [nome for nome, qtd in personagem.pocoes.items() if qtd > 0]
  if not opcoes_pocao:
    escrever(f'{Cor.VERMELHO}Você não tem poções.{Cor.RESET}')
    return
  escolha = ler_acao('Qual poção usar?', opcoes_pocao)
  if escolha is not None:
    inventario.usar_pocao(personagem, opcoes_pocao[escolha], em_batalha=True, escrever=escrever)


def batalhar(personagem, monstro_base, escrever=None, ler_acao=None, aguardar=None, elite=False):
  """Roda uma batalha inteira e devolve (ResultadoBatalha.*, MonstroBatalha)."""
  escrever = escrever or print
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura

  monstro = MonstroBatalha.instanciar(monstro_base, elite=elite)
  personagem.local = 'batalha'
  personagem.bonus_dano_batalha = 0
  personagem.bonus_esquiva_batalha = 0
  personagem.bonus_critico_batalha = 0
  personagem.pocao_poder_usada = False
  personagem.pocao_esquiva_usada = False
  personagem.pocao_furia_usada = False
  for nome_habilidade in personagem.habilidades_equipadas:
    personagem.cooldowns[nome_habilidade] = 0

  for nome_efeito, turnos in equipamento.efeitos_iniciais_de_batalha_acessorios(personagem):
    if _efeito_grudou():
      efeitos.aplicar_efeito(monstro.efeitos_ativos, nome_efeito, turnos)
      escrever(f'{Cor.VERMELHO}Seu acessório inflige {nome_efeito} no {monstro.nome} '
               f'assim que a batalha começa!{Cor.RESET}')

  sufixo_elite = f' {Cor.AMARELO}(ELITE){Cor.RESET}' if elite else ''
  escrever(f'{Cor.BRANCO}Você entrou em batalha contra {monstro.nome}!{Cor.RESET}{sufixo_elite}')
  aguardar()

  turnos_auto_restantes = 0

  while True:
    if personagem.vida <= 0:
      return ResultadoBatalha.DERROTA, monstro
    if not monstro.vivo:
      return ResultadoBatalha.VITORIA, monstro

    if turnos_auto_restantes > 0 and personagem.vida_percentual() * 100 < AUTOBATALHA_VIDA_MINIMA_PERCENTUAL:
      turnos_auto_restantes = 0
      escrever(f'{Cor.AMARELO}Autobatalha cancelada — sua vida está baixa demais.{Cor.RESET}')

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
      return ResultadoBatalha.DERROTA, monstro

    habilidades_ativas = [HABILIDADES[nome] for nome in personagem.habilidades_equipadas]

    # Fase de escolha: repete em caso de escolha inválida, sem passar a vez.
    while True:
      if turnos_auto_restantes > 0:
        turnos_auto_restantes -= 1
        melhor = _melhor_habilidade_disponivel(personagem, habilidades_ativas, monstro)
        if melhor is None:
          escrever(f'{Cor.CIANO}Autobatalha: nenhuma habilidade disponível, pulando a vez.{Cor.RESET}')
          break
        if melhor.custo_furia > 0:
          personagem.furia_cavaleiro -= melhor.custo_furia
        else:
          personagem.mana -= melhor.mana
        personagem.cooldowns[melhor.nome] = melhor.cooldown_max
        personagem_ataca(personagem, melhor, monstro, escrever)
        break

      labels = [_descricao_habilidade(personagem, h, monstro) for h in habilidades_ativas]
      acoes = ['habilidade'] * len(habilidades_ativas)

      proxima_postura = 'defensiva' if personagem.postura == 'ofensiva' else 'ofensiva'
      labels.append(f'Mudar postura para {proxima_postura} (atual: {personagem.postura})')
      acoes.append('postura')
      labels += [f'Autobatalha ({AUTOBATALHA_TURNOS} turnos)', 'Itens', 'Pular a vez', 'Tentar fugir']
      acoes += ['autobatalha', 'itens', 'pular', 'fugir']

      escolha = ler_acao(_tela_batalha(personagem, monstro), labels, com_voltar=False)
      tipo_acao = acoes[escolha]

      if tipo_acao == 'autobatalha':
        turnos_auto_restantes = AUTOBATALHA_TURNOS
        escrever(f'{Cor.CIANO}Autobatalha ativada por {AUTOBATALHA_TURNOS} turnos.{Cor.RESET}')
        continue

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
        else:
          if personagem.mana < habilidade.mana:
            escrever(f'{Cor.VERMELHO}Mana insuficiente.{Cor.RESET}')
            aguardar()
            continue
          personagem.mana -= habilidade.mana
        personagem.cooldowns[habilidade.nome] = habilidade.cooldown_max
        personagem_ataca(personagem, habilidade, monstro, escrever)
        break

      if tipo_acao == 'postura':
        personagem.postura = proxima_postura
        escrever(f'Você muda para postura {Cor.BRANCO}{proxima_postura}{Cor.RESET}.')
        aguardar()
        continue  # trocar de postura é de graça — não passa a vez pro monstro

      if tipo_acao == 'itens':
        _abrir_itens_de_batalha(personagem, escrever, ler_acao)
        aguardar()
        continue

      if tipo_acao == 'pular':
        escrever('Você pula a vez.')
      elif tipo_acao == 'fugir':
        if random.randint(1, 5) == 1:
          escrever(f'{Cor.VERDE}Você fugiu com sucesso!{Cor.RESET}')
          aguardar()
          return ResultadoBatalha.FUGA, monstro
        escrever(f'{Cor.VERMELHO}Você não conseguiu fugir!{Cor.RESET}')
      break

    mana_max = equipamento.mana_maxima_efetiva(personagem)
    personagem.mana = min(mana_max, personagem.mana + round(mana_max * 0.1))

    if not monstro.vivo:
      aguardar()
      return ResultadoBatalha.VITORIA, monstro

    # Queimadura/Sangramento/Veneno/Regeneração aplicados NO monstro nunca
    # eram processados — só os efeitos do próprio jogador tinham esse tratamento.
    monstro.vida = efeitos.processar_efeitos_continuos(
        monstro.efeitos_ativos, monstro.vida, escrever, monstro.nome,
        vida_maxima=round(monstro.base.vida_maxima * (1.8 if monstro.elite else 1.0)))
    if not monstro.vivo:
      aguardar()
      return ResultadoBatalha.VITORIA, monstro

    monstro_fugiu = monstro_ataca(personagem, monstro, escrever)
    aguardar()
    if monstro_fugiu:
      return ResultadoBatalha.MONSTRO_FUGIU, monstro
    if personagem.vida <= 0:
      return ResultadoBatalha.DERROTA, monstro

    for nome in personagem.cooldowns:
      if personagem.cooldowns[nome] > 0:
        personagem.cooldowns[nome] -= 1
