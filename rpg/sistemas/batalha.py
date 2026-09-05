"""Loop de batalha. Antes cada turno era resolvido chamando a função de batalha
de novo recursivamente (e ela nunca "retornava" de verdade) — aqui é um `while`
comum, então o jogo não acumula profundidade de recursão a cada turno.
"""

import random

from ..config import (CHANCE_CRITICO_BASE, FOME_CRITICA, Cor, MULTIPLICADOR_CRITICO,
                       MULTIPLICADOR_FRAQUEZA_ELEMENTAL,
                       MULTIPLICADOR_RESISTENCIA_ELEMENTAL)
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


def multiplicador_elemental(elemento_ataque, monstro):
  if elemento_ataque in monstro.base.fraquezas:
    return MULTIPLICADOR_FRAQUEZA_ELEMENTAL
  if elemento_ataque in monstro.base.resistencias:
    return MULTIPLICADOR_RESISTENCIA_ELEMENTAL
  return 1.0


def chance_de_critico(personagem, habilidade):
  return (CHANCE_CRITICO_BASE + habilidade.bonus_critico + personagem.sorte
          + personagem.bonus_critico_batalha
          + equipamento.chance_critico_extra_acessorio(personagem))


def _dano_base(personagem, habilidade, monstro):
  """Dano determinístico (sem rolar crítico) — reaproveitado tanto pelo
  cálculo real quanto pela prévia mostrada no menu de batalha."""
  arma = equipamento.resolver_arma(personagem)
  dano = float(habilidade.dano_base)
  dano += dano * (personagem.poder * 3) / 100
  dano += dano * arma.bonus_poder_percentual / 100
  if personagem.bonus_dano_batalha:
    dano += dano * personagem.bonus_dano_batalha / 100

  debuff = efeitos.bonus_debuff_poder(personagem.efeitos_ativos)
  if debuff:
    dano -= dano * debuff / 100

  if personagem.eten:
    dano += dano * 30 / 100

  if personagem.fome <= FOME_CRITICA:
    dano -= dano * 10 / 100

  raca = RACAS.get(personagem.raca)
  if raca and raca.bonus_tipo == 'poder':
    dano += dano * raca.valor / 100

  return dano * multiplicador_elemental(habilidade.elemento, monstro)


def calcular_dano(personagem, habilidade, monstro):
  dano = _dano_base(personagem, habilidade, monstro)
  critico = random.randint(1, 100) <= chance_de_critico(personagem, habilidade)
  if critico:
    dano *= MULTIPLICADOR_CRITICO
  return max(1, round(dano)), critico


def prever_dano(personagem, habilidade, monstro):
  """Estimativa sem crítico, só para exibir no menu de batalha."""
  return max(1, round(_dano_base(personagem, habilidade, monstro)))


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

  if habilidade.efeito and monstro.vivo:
    valor = 15 if habilidade.efeito == 'Fraqueza' else 0
    efeitos.aplicar_efeito(monstro.efeitos_ativos, habilidade.efeito, habilidade.turnos_efeito, valor)
    escrever(f'{Cor.VERMELHO}O {monstro.nome} sofreu {habilidade.efeito}!{Cor.RESET}')


def monstro_ataca(personagem, monstro, escrever):
  if efeitos.verificar_paralisia(monstro.efeitos_ativos, escrever, monstro.nome):
    return

  esquiva = personagem.esquiva + personagem.bonus_esquiva_batalha
  if random.randint(1, 100) <= esquiva:
    escrever(f'{Cor.AMARELO}Você esquiva do ataque do monstro!{Cor.RESET}')
    return

  dano = random.randint(monstro.base.ataque_min, monstro.base.ataque_max)
  descricao = random.choice(monstro.base.descricoes_ataque)
  personagem.vida = max(0, personagem.vida - dano)
  escrever(f'{descricao}, causando {Cor.VERMELHO}{dano} de dano{Cor.RESET} em você.')

  if monstro.base.efeito_aplicado and random.randint(1, 2) == 1:
    efeitos.aplicar_efeito(personagem.efeitos_ativos, monstro.base.efeito_aplicado,
                            monstro.base.turnos_efeito_aplicado)
    escrever(f'{Cor.VERMELHO}Você sofreu {monstro.base.efeito_aplicado}!{Cor.RESET}')


def _tela_batalha(personagem, monstro):
  vida_max = equipamento.vida_maxima_efetiva(personagem)
  mana_max = equipamento.mana_maxima_efetiva(personagem)
  return (f'  {Cor.BRANCO}Batalha contra {monstro.nome}{Cor.RESET}\n'
          f'  Vida do inimigo: {barra(monstro.vida, monstro.base.vida_maxima, cor=Cor.VERMELHO)}\n\n'
          f'  Sua vida: {barra(personagem.vida, vida_max, cor=Cor.VERMELHO)}\n'
          f'  Sua mana: {barra(personagem.mana, mana_max, cor=Cor.AZUL)}\n')


def _descricao_habilidade(personagem, habilidade, monstro):
  cd = personagem.cooldowns.get(habilidade.nome, 0)
  estado = f'{Cor.VERMELHO}[Cooldown: {cd}]{Cor.RESET}' if cd > 0 else f'{Cor.VERDE}Pronta{Cor.RESET}'
  dano_previsto = prever_dano(personagem, habilidade, monstro)
  efeito = f' | Efeito: {habilidade.efeito} ({habilidade.turnos_efeito}t)' if habilidade.efeito else ''
  return (f'{Cor.BRANCO}{habilidade.nome}{Cor.RESET} — '
          f'{Cor.AZUL}{habilidade.mana} mana{Cor.RESET}, '
          f'{Cor.VERMELHO}~{dano_previsto} dano{Cor.RESET} '
          f'({habilidade.elemento}){efeito} — {estado}')


def _abrir_itens_de_batalha(personagem, escrever, ler_acao):
  opcoes_pocao = [nome for nome, qtd in personagem.pocoes.items() if qtd > 0]
  if not opcoes_pocao:
    escrever(f'{Cor.VERMELHO}Você não tem poções.{Cor.RESET}')
    return
  escolha = ler_acao('Qual poção usar?', opcoes_pocao)
  if escolha is not None:
    inventario.usar_pocao(personagem, opcoes_pocao[escolha], em_batalha=True, escrever=escrever)


def batalhar(personagem, monstro_base, escrever=None, ler_acao=None, aguardar=None):
  """Roda uma batalha inteira e devolve (ResultadoBatalha.*, MonstroBatalha)."""
  escrever = escrever or print
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura

  monstro = MonstroBatalha.instanciar(monstro_base)
  personagem.local = 'batalha'
  personagem.bonus_dano_batalha = 0
  personagem.bonus_esquiva_batalha = 0
  personagem.bonus_critico_batalha = 0
  personagem.pocao_poder_usada = False
  personagem.pocao_esquiva_usada = False
  personagem.pocao_furia_usada = False
  for nome_habilidade in personagem.habilidades_equipadas:
    personagem.cooldowns[nome_habilidade] = 0

  efeito_inicial = equipamento.efeito_inicial_de_batalha_acessorio(personagem)
  if efeito_inicial:
    nome_efeito, turnos = efeito_inicial
    efeitos.aplicar_efeito(monstro.efeitos_ativos, nome_efeito, turnos)
    escrever(f'{Cor.VERMELHO}Seu acessório inflige {nome_efeito} no {monstro.nome} '
             f'assim que a batalha começa!{Cor.RESET}')

  escrever(f'{Cor.BRANCO}Você entrou em batalha contra {monstro.nome}!{Cor.RESET}')
  aguardar()

  while True:
    if personagem.vida <= 0:
      return ResultadoBatalha.DERROTA, monstro
    if not monstro.vivo:
      return ResultadoBatalha.VITORIA, monstro

    personagem.vida = efeitos.processar_efeitos_continuos(
        personagem.efeitos_ativos, personagem.vida, escrever, 'Você')
    if personagem.vida <= 0:
      aguardar()
      return ResultadoBatalha.DERROTA, monstro

    habilidades_ativas = [HABILIDADES[nome] for nome in personagem.habilidades_equipadas]

    # Fase de escolha: repete em caso de escolha inválida, sem passar a vez.
    while True:
      opcoes = [_descricao_habilidade(personagem, h, monstro) for h in habilidades_ativas]
      opcoes += ['Itens', 'Pular a vez', 'Tentar fugir']

      escolha = ler_acao(_tela_batalha(personagem, monstro), opcoes, com_voltar=False)

      if escolha < len(habilidades_ativas):
        habilidade = habilidades_ativas[escolha]
        if personagem.cooldowns.get(habilidade.nome, 0) > 0:
          escrever(f'{Cor.VERMELHO}Essa habilidade ainda está em cooldown.{Cor.RESET}')
          aguardar()
          continue
        if personagem.mana < habilidade.mana:
          escrever(f'{Cor.VERMELHO}Mana insuficiente.{Cor.RESET}')
          aguardar()
          continue
        personagem.mana -= habilidade.mana
        personagem.cooldowns[habilidade.nome] = habilidade.cooldown_max
        personagem_ataca(personagem, habilidade, monstro, escrever)
        break

      acao = ['Itens', 'Pular a vez', 'Tentar fugir'][escolha - len(habilidades_ativas)]
      if acao == 'Itens':
        _abrir_itens_de_batalha(personagem, escrever, ler_acao)
        aguardar()
        continue
      if acao == 'Pular a vez':
        escrever('Você pula a vez.')
      elif acao == 'Tentar fugir':
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

    monstro_ataca(personagem, monstro, escrever)
    aguardar()
    if personagem.vida <= 0:
      return ResultadoBatalha.DERROTA, monstro

    for nome in personagem.cooldowns:
      if personagem.cooldowns[nome] > 0:
        personagem.cooldowns[nome] -= 1
