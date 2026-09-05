"""Conversão de moedas e missões da guilda.

No jogo original havia 4 blocos quase idênticos (~35 linhas cada) para
cobre→prata, prata→cobre, prata→ouro, ouro→prata. Aqui é uma função só.
A recompensa de missão também era um `if/elif` fixo por nome de monstro —
agora é uma fórmula baseada no nível real do monstro, então funciona
automaticamente para qualquer monstro novo que a gente adicionar.
"""

import random

from ..dados.monstros import MONSTROS

TAXA_CONVERSAO = 1000
_ORDEM_MOEDAS = ['cobre', 'prata', 'ouro']


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


def gerar_missoes(personagem):
  candidatos = [nome for nome, m in MONSTROS.items()
                if not m.chefe and m.nivel <= personagem.nivel + 10]
  if not candidatos:
    candidatos = [nome for nome, m in MONSTROS.items() if not m.chefe]

  missoes = []
  for _ in range(3):
    nome_monstro = random.choice(candidatos)
    monstro = MONSTROS[nome_monstro]
    quantidade = random.randint(1, 5)
    missoes.append({
      'monstro': nome_monstro,
      'quantidade': quantidade,
      'recompensa_exp': quantidade * monstro.nivel * 2,
      'recompensa_moedas': quantidade * monstro.nivel * 3,
    })
  return missoes


def aceitar_missao(personagem, missao):
  personagem.missao_monstro = missao['monstro']
  personagem.missao_quantidade_alvo = missao['quantidade']
  personagem.missao_quantidade_atual = 0
  personagem.missao_recompensa_exp = missao['recompensa_exp']
  personagem.missao_recompensa_moedas = missao['recompensa_moedas']


def abandonar_missao(personagem):
  personagem.missao_monstro = ''
  personagem.missao_quantidade_alvo = 0
  personagem.missao_quantidade_atual = 0
  personagem.missao_recompensa_exp = 0
  personagem.missao_recompensa_moedas = 0
