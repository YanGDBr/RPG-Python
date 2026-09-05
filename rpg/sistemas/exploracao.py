"""Exploração de um andar de dungeon. Uma função só, genérica pra qualquer
andar de qualquer dungeon — o bug antigo (andar 2 sorteando monstro do andar 1
porque cada andar tinha sua própria função copiada e colada) não existe mais
porque aqui só existe ESTA função, parametrizada pelos dados do andar.

Cada andar tem seu próprio mapa desenhado (rpg/dados/mapas.py), com paredes de
verdade bloqueando passagem — bem diferente da grade genérica de pontinhos
que existia antes, onde todo andar era visualmente idêntico.
"""

import random

from ..config import Cor
from ..dados.dungeons import DUNGEONS
from ..dados.mapas import MAPAS
from ..dados.monstros import MONSTROS
from ..entrada import aguardar_leitura, ler_tecla, perguntar_sim_nao
from ..interface import limpar_tela
from . import equipamento
from .batalha import ResultadoBatalha, batalhar
from .equipamento import chance_boss_extra_acessorio
from .inventario import consumir_efeito_ativado
from .progressao import aplicar_desgaste_fome, conceder_recompensas, verificar_morte

CELULAS_ANDAVEIS = ('.', '?', 'E')

DESLOCAMENTOS = {
  'cima': (-1, 0), 'w': (-1, 0),
  'baixo': (1, 0), 's': (1, 0),
  'esquerda': (0, -1), 'a': (0, -1),
  'direita': (0, 1), 'd': (0, 1),
}


def _encontrar_entrada(mapa):
  for y, linha in enumerate(mapa):
    x = linha.find('E')
    if x != -1:
      return [y, x]
  raise ValueError('mapa sem entrada (E)')


def _desenhar_mapa(mapa, posicao, andar, personagem):
  linhas = [f'  {equipamento.resumo_status(personagem)}\n',
            f'  {Cor.BRANCO}{andar.nome}{Cor.RESET} — Andar {andar.numero} ({andar.faixa_nivel})\n']
  for y, linha in enumerate(mapa):
    celulas = []
    for x, caractere in enumerate(linha):
      if [y, x] == posicao:
        celulas.append(f'{Cor.VERDE}@{Cor.RESET}')
      elif caractere == '?':
        celulas.append(f'{Cor.AMARELO}?{Cor.RESET}')
      elif caractere in ('.', 'E'):
        celulas.append('.')
      else:
        celulas.append(f'{Cor.CINZA}{caractere}{Cor.RESET}')
    linhas.append(' '.join(celulas))
  linhas.append('\nWASD ou setas para andar — Esc para voltar sem explorar.')
  return '\n'.join(linhas)


def explorar(personagem, dungeon_id, *, escrever=None, leitor_tecla=None, limpar=None,
             ler_confirmacao=None, ler_acao_batalha=None, aguardar=None):
  """Uma sessão de exploração: anda pelo mapa do andar até pisar num ponto de
  interesse (ou desistir com Esc).

  `ler_acao_batalha` e `aguardar` são repassados adiante (até dentro de uma
  eventual batalha) — sem isso, testes automatizados travariam esperando
  teclado/Enter reais.
  """
  escrever = escrever or print
  leitor_tecla = leitor_tecla or ler_tecla
  limpar = limpar or limpar_tela
  ler_confirmacao = ler_confirmacao or perguntar_sim_nao
  aguardar = aguardar or aguardar_leitura

  dungeon = DUNGEONS[dungeon_id]
  andar = dungeon.andares[personagem.andar_atual[dungeon_id] - 1]
  mapa = MAPAS[dungeon_id][andar.numero]
  posicao = _encontrar_entrada(mapa)
  altura, largura = len(mapa), len(mapa[0])

  while True:
    limpar()
    escrever(_desenhar_mapa(mapa, posicao, andar, personagem))
    tecla = leitor_tecla()
    if tecla == 'esc':
      return
    deslocamento = DESLOCAMENTOS.get(tecla)
    if deslocamento is None:
      continue
    novo_y, novo_x = posicao[0] + deslocamento[0], posicao[1] + deslocamento[1]
    if not (0 <= novo_y < altura and 0 <= novo_x < largura):
      continue
    if mapa[novo_y][novo_x] not in CELULAS_ANDAVEIS:
      continue
    posicao = [novo_y, novo_x]
    if mapa[posicao[0]][posicao[1]] == '?':
      break

  limpar()
  aplicar_desgaste_fome(personagem, escrever)
  _resolver_evento(personagem, dungeon_id, andar, escrever, ler_confirmacao, ler_acao_batalha, aguardar)
  aguardar()


def _resolver_evento(personagem, dungeon_id, andar, escrever, ler_confirmacao,
                      ler_acao_batalha, aguardar):
  chance_boss = andar.chance_encontrar_chefe
  bonus_acessorio = chance_boss_extra_acessorio(personagem)
  if bonus_acessorio:
    chance_boss = bonus_acessorio
    escrever(f'{Cor.CIANO}Seu acessório aumenta a chance de achar a sala do chefe!{Cor.RESET}')

  if random.randint(1, chance_boss) == 1:
    pergunta = (f'{Cor.AMARELO}Você encontrou a sala do chefe: {andar.chefe}!{Cor.RESET}\n'
                f'Deseja entrar para batalhar?')
    if ler_confirmacao(pergunta):
      _lutar(personagem, dungeon_id, andar.chefe, escrever, ler_acao_batalha, aguardar)
    return

  peso_monstro = 3
  valor_monstro = consumir_efeito_ativado(personagem, 'monstro')
  valor_anti = consumir_efeito_ativado(personagem, 'anti_monstro')
  if valor_monstro:
    peso_monstro += valor_monstro
    escrever(f'{Cor.CIANO}O item que você usou aumenta a chance de encontrar um monstro.{Cor.RESET}')
  if valor_anti:
    peso_monstro = max(1, peso_monstro - valor_anti)
    escrever(f'{Cor.CIANO}O item que você usou reduz a chance de encontrar um monstro.{Cor.RESET}')

  if random.randint(1, peso_monstro + 2) <= peso_monstro:
    pool = list(andar.monstros_comuns)
    if personagem.missao_monstro and personagem.missao_monstro in andar.monstros_comuns:
      # Dobra a chance do monstro da missão ativa aparecer, senão ele só
      # aparecia na mesma proporção dos outros e a missão nunca avançava.
      pool += [personagem.missao_monstro] * len(andar.monstros_comuns)
    nome_monstro = random.choice(pool)
    pergunta = f'{Cor.AMARELO}Você encontrou um {nome_monstro}!{Cor.RESET}\nDeseja lutar contra ele?'
    if ler_confirmacao(pergunta):
      _lutar(personagem, dungeon_id, nome_monstro, escrever, ler_acao_batalha, aguardar)
    return

  if random.randint(1, 2) == 1:
    moedas = random.randint(5, 15 + andar.numero * 5)
    personagem.moeda_cobre += moedas
    escrever(f'{Cor.VERDE}Você encontrou {moedas} cobres!{Cor.RESET}')
  else:
    escrever(f'{Cor.CINZA}Você explorou a dungeon e não encontrou nada.{Cor.RESET}')


def _lutar(personagem, dungeon_id, nome_monstro, escrever, ler_acao_batalha, aguardar):
  resultado, monstro = batalhar(personagem, MONSTROS[nome_monstro], escrever=escrever,
                                 ler_acao=ler_acao_batalha, aguardar=aguardar)
  personagem.local = f'dungeon:{dungeon_id}'
  if resultado == ResultadoBatalha.VITORIA:
    escrever(f'{Cor.VERDE}Você derrotou {monstro.nome}!{Cor.RESET}')
    conceder_recompensas(personagem, monstro.base, escrever)
  elif resultado == ResultadoBatalha.DERROTA:
    verificar_morte(personagem, escrever)
