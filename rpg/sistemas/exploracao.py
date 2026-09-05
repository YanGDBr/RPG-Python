"""Exploração de um andar de dungeon. Uma função só, genérica pra qualquer
andar de qualquer dungeon — o bug antigo (andar 2 sorteando monstro do andar 1
porque cada andar tinha sua própria função copiada e colada) não existe mais
porque aqui só existe ESTA função, parametrizada pelos dados do andar.
"""

import random

from ..config import Cor
from ..dados.dungeons import DUNGEONS
from ..dados.monstros import MONSTROS
from ..entrada import aguardar_leitura, ler_tecla, perguntar_sim_nao
from ..interface import limpar_tela
from .batalha import ResultadoBatalha, batalhar
from .equipamento import chance_boss_extra_acessorio
from .inventario import consumir_efeito_ativado
from .progressao import aplicar_desgaste_fome, conceder_recompensas, verificar_morte

TAMANHO_MAPA = 6

DESLOCAMENTOS = {
  'cima': (-1, 0), 'w': (-1, 0),
  'baixo': (1, 0), 's': (1, 0),
  'esquerda': (0, -1), 'a': (0, -1),
  'direita': (0, 1), 'd': (0, 1),
}


def _desenhar_mapa(posicao, andar):
  linhas = [f'  Explorando o Andar {andar.numero} — {andar.faixa_nivel}\n']
  for y in range(TAMANHO_MAPA):
    linha = ''
    for x in range(TAMANHO_MAPA):
      linha += ' @ ' if [y, x] == posicao else ' . '
    linhas.append(linha)
  linhas.append('\nWASD ou setas para andar — Esc para voltar sem explorar.')
  return '\n'.join(linhas)


def explorar(personagem, dungeon_id, *, escrever=None, leitor_tecla=None, limpar=None,
             ler_confirmacao=None, ler_acao_batalha=None, aguardar=None):
  """Uma sessão de exploração: anda pelo mapa até topar com algo.

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

  posicao = [random.randint(0, TAMANHO_MAPA - 1), random.randint(0, TAMANHO_MAPA - 1)]
  passos_ate_evento = random.randint(3, 6)
  passos = 0

  while passos < passos_ate_evento:
    limpar()
    escrever(_desenhar_mapa(posicao, andar))
    tecla = leitor_tecla()
    if tecla == 'esc':
      return
    deslocamento = DESLOCAMENTOS.get(tecla)
    if deslocamento is None:
      continue
    novo_y = max(0, min(TAMANHO_MAPA - 1, posicao[0] + deslocamento[0]))
    novo_x = max(0, min(TAMANHO_MAPA - 1, posicao[1] + deslocamento[1]))
    if [novo_y, novo_x] != posicao:
      posicao = [novo_y, novo_x]
      passos += 1

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
    nome_monstro = random.choice(andar.monstros_comuns)
    pergunta = f'{Cor.AMARELO}Você encontrou um {nome_monstro}!{Cor.RESET}\nDeseja lutar contra ele?'
    if ler_confirmacao(pergunta):
      _lutar(personagem, dungeon_id, nome_monstro, escrever, ler_acao_batalha, aguardar)
    return

  if random.randint(1, 2) == 1:
    moedas = random.randint(5, 15 + andar.numero * 5)
    personagem.moeda_cobre += moedas
    escrever(f'{Cor.VERDE}Você encontrou {moedas} moedas de cobre!{Cor.RESET}')
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
