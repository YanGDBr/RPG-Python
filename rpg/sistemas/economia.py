"""Conversão de moedas e missões da guilda.

No jogo original havia 4 blocos quase idênticos (~35 linhas cada) para
cobre→prata, prata→cobre, prata→ouro, ouro→prata. Aqui é uma função só.
A recompensa de missão também era um `if/elif` fixo por nome de monstro —
agora é uma fórmula baseada no nível real do monstro, então funciona
automaticamente para qualquer monstro novo que a gente adicionar.
"""

import random
from math import trunc

from ..config import (MAX_MISSOES_ATIVAS, MULTIPLICADOR_EXP_GLOBAL,
                       QUANTIDADE_MISSOES_POR_QUADRO, REPUTACAO_TIERS)
from ..dados.dungeons import DUNGEONS
from ..dados.monstros import MONSTROS

TAXA_CONVERSAO = 1000
_ORDEM_MOEDAS = ['cobre', 'prata', 'ouro']


def tier_reputacao(reputacao):
  """Índice e nome do tier de reputação atual — cada tier acima do primeiro
  deixa as missões da guilda mais recompensadoras."""
  indice, nome = 0, REPUTACAO_TIERS[0][1]
  for i, (minimo, nome_tier) in enumerate(REPUTACAO_TIERS):
    if reputacao >= minimo:
      indice, nome = i, nome_tier
  return indice, nome


def converter(personagem, origem, destino, quantidade):
  if origem not in _ORDEM_MOEDAS or destino not in _ORDEM_MOEDAS:
    return False, 'Moeda inválida.'

  saldo_attr, destino_attr = f'moeda_{origem}', f'moeda_{destino}'
  saldo = getattr(personagem, saldo_attr)
  if quantidade <= 0 or quantidade > saldo:
    return False, 'Quantidade inválida ou maior do que você possui.'

  indice_origem, indice_destino = _ORDEM_MOEDAS.index(origem), _ORDEM_MOEDAS.index(destino)

  if indice_destino == indice_origem + 1:
    if quantidade % TAXA_CONVERSAO != 0:
      return False, f'Só é possível converter em múltiplos de {TAXA_CONVERSAO}.'
    setattr(personagem, saldo_attr, saldo - quantidade)
    setattr(personagem, destino_attr, getattr(personagem, destino_attr) + quantidade // TAXA_CONVERSAO)
    return True, 'Conversão realizada com sucesso.'

  if indice_destino == indice_origem - 1:
    setattr(personagem, saldo_attr, saldo - quantidade)
    setattr(personagem, destino_attr, getattr(personagem, destino_attr) + quantidade * TAXA_CONVERSAO)
    return True, 'Conversão realizada com sucesso.'

  return False, 'Só é possível converter entre moedas vizinhas (cobre <-> prata <-> ouro).'


def gerar_missoes_do_andar(personagem, dungeon_id, andar_numero):
  """O quadro de missões de um andar específico — só sorteia entre os
  monstros comuns daquele andar, então o quadro sempre bate com o que o
  jogador está de fato enfrentando ali."""
  andar = DUNGEONS[dungeon_id].andares[andar_numero - 1]
  indice_tier, _ = tier_reputacao(personagem.reputacao_guilda)
  bonus_tier_percentual = indice_tier * 10

  missoes = []
  for indice_quadro in range(QUANTIDADE_MISSOES_POR_QUADRO):
    nome_monstro = random.choice(andar.monstros_comuns)
    monstro = MONSTROS[nome_monstro]
    quantidade = random.randint(1, 5)
    missoes.append({
      'dungeon_id': dungeon_id,
      'andar': andar_numero,
      'quadro_indice': indice_quadro,
      'monstro': nome_monstro,
      'quantidade_alvo': quantidade,
      'recompensa_exp': trunc(quantidade * monstro.nivel * 2 * MULTIPLICADOR_EXP_GLOBAL
                               * (1 + bonus_tier_percentual / 100)),
      'recompensa_moedas': trunc(quantidade * monstro.nivel * 3 * (1 + bonus_tier_percentual / 100)),
    })
  return missoes


def missao_equipada(personagem, missao):
  return any(m['dungeon_id'] == missao['dungeon_id'] and m['andar'] == missao['andar']
             and m['quadro_indice'] == missao['quadro_indice'] for m in personagem.missoes_ativas)


def aceitar_missao(personagem, missao):
  if len(personagem.missoes_ativas) >= MAX_MISSOES_ATIVAS:
    return False
  personagem.missoes_ativas.append({**missao, 'quantidade_atual': 0})
  return True


def abandonar_missao(personagem, indice):
  if 0 <= indice < len(personagem.missoes_ativas):
    del personagem.missoes_ativas[indice]
