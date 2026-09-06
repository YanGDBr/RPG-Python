"""Exploração de um andar de dungeon. Uma função só, genérica pra qualquer
andar de qualquer dungeon — o bug antigo (andar 2 sorteando monstro do andar 1
porque cada andar tinha sua própria função copiada e colada) não existe mais
porque aqui só existe ESTA função, parametrizada pelos dados do andar.

Cada andar tem seu próprio mapa desenhado (rpg/dados/mapas.py), com paredes de
verdade bloqueando passagem — bem diferente da grade genérica de pontinhos
que existia antes, onde todo andar era visualmente idêntico.
"""

import random
from collections import Counter

from ..config import (CHANCE_GRUPO_MONSTROS, CHANCE_MONSTRO_ELITE, NIVEL_PERIGO_AMARELO,
                       NIVEL_PERIGO_VERDE, NIVEL_PERIGO_VERMELHO, TAMANHO_GRUPO_MONSTROS_MAX,
                       TAMANHO_GRUPO_MONSTROS_MIN, Cor)
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


_COR_PERIGO = {
  NIVEL_PERIGO_VERDE: Cor.VERDE,
  NIVEL_PERIGO_AMARELO: Cor.AMARELO,
  NIVEL_PERIGO_VERMELHO: Cor.VERMELHO,
}


def _calcular_niveis_perigo(mapa):
  """Cada ponto de interesse (`?`) do andar recebe um dos 3 níveis de perigo,
  calculado pela distância até a entrada (mais longe, mais perigoso) — não
  precisa de nenhum dado extra por mapa, e continua funcionando pra qualquer
  andar novo que a gente desenhar."""
  entrada = tuple(_encontrar_entrada(mapa))
  pontos = [(y, x) for y, linha in enumerate(mapa) for x, c in enumerate(linha) if c == '?']
  pontos.sort(key=lambda p: abs(p[0] - entrada[0]) + abs(p[1] - entrada[1]))
  total = len(pontos)
  niveis = {}
  for indice, ponto in enumerate(pontos):
    if indice < total / 3:
      niveis[ponto] = NIVEL_PERIGO_VERDE
    elif indice < total * 2 / 3:
      niveis[ponto] = NIVEL_PERIGO_AMARELO
    else:
      niveis[ponto] = NIVEL_PERIGO_VERMELHO
  return niveis


def _desenhar_mapa(mapa, posicao, andar, personagem):
  niveis_perigo = _calcular_niveis_perigo(mapa)
  linhas = [f'  {equipamento.resumo_status(personagem)}\n',
            f'  {Cor.BRANCO}{andar.nome}{Cor.RESET} — Andar {andar.numero} ({andar.faixa_nivel})\n']
  for y, linha in enumerate(mapa):
    celulas = []
    for x, caractere in enumerate(linha):
      if [y, x] == posicao:
        celulas.append(f'{Cor.VERDE}@{Cor.RESET}')
      elif caractere == '?':
        cor = _COR_PERIGO.get(niveis_perigo.get((y, x)), Cor.AMARELO)
        celulas.append(f'{cor}?{Cor.RESET}')
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
  nivel_perigo = _calcular_niveis_perigo(mapa).get(tuple(posicao))
  _resolver_evento(personagem, dungeon_id, andar, escrever, ler_confirmacao, ler_acao_batalha, aguardar,
                    nivel_perigo)
  aguardar()


def _resolver_evento(personagem, dungeon_id, andar, escrever, ler_confirmacao,
                      ler_acao_batalha, aguardar, nivel_perigo=None):
  """`nivel_perigo` (verde/amarelo/vermelho, ver config.py) só existe quando
  chamado a partir de `explorar()`, que sabe em qual ponto do mapa o jogador
  pisou — sem ele, o comportamento é o padrão de sempre (usado nos testes que
  chamam essa função direto, sem simular um mapa)."""
  chance_boss = andar.chance_encontrar_chefe
  if nivel_perigo == NIVEL_PERIGO_AMARELO:
    chance_boss = max(1, chance_boss - 2)
  elif nivel_perigo == NIVEL_PERIGO_VERMELHO:
    chance_boss = max(1, chance_boss - 4)
  bonus_acessorio = chance_boss_extra_acessorio(personagem)
  if bonus_acessorio:
    chance_boss = min(chance_boss, bonus_acessorio)
    escrever(f'{Cor.CIANO}Seu acessório aumenta a chance de achar a sala do chefe!{Cor.RESET}')

  bonus_mapa = consumir_efeito_ativado(personagem, 'boss_mapa')
  if bonus_mapa:
    chance_boss = min(chance_boss, bonus_mapa)
    escrever(f'{Cor.CIANO}O Mapa do Tesouro aumenta a chance de achar a sala do chefe!{Cor.RESET}')

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
    # Área verde: puxa pros monstros mais simples do andar (primeira metade da
    # lista); vermelha/amarela: puxa pros mais fortes (segunda metade).
    metade = max(1, len(pool) // 2)
    if nivel_perigo == NIVEL_PERIGO_VERDE:
      pool = pool[:metade]
    elif nivel_perigo in (NIVEL_PERIGO_AMARELO, NIVEL_PERIGO_VERMELHO):
      pool = pool[-metade:]
    # Dobra a chance de cada monstro com missão ativa aparecer, senão eles só
    # apareciam na mesma proporção dos outros e a missão nunca avançava.
    monstros_com_missao = {m['monstro'] for m in personagem.missoes_ativas} & set(andar.monstros_comuns)
    for nome_monstro_missao in monstros_com_missao:
      pool += [nome_monstro_missao] * len(andar.monstros_comuns)

    # Grupos (2-3 monstros comuns, nunca chefe) ficam mais prováveis quanto
    # mais perigosa a área — e nunca viram elite (já são mais perigosos por
    # serem vários de uma vez).
    chance_grupo = CHANCE_GRUPO_MONSTROS
    if nivel_perigo == NIVEL_PERIGO_VERDE:
      chance_grupo += 2
    elif nivel_perigo == NIVEL_PERIGO_VERMELHO:
      chance_grupo = max(2, CHANCE_GRUPO_MONSTROS - 2)
    eh_grupo = random.randint(1, chance_grupo) == 1

    if eh_grupo:
      tamanho = random.randint(TAMANHO_GRUPO_MONSTROS_MIN, TAMANHO_GRUPO_MONSTROS_MAX)
      nomes_monstros = [random.choice(pool) for _ in range(tamanho)]
      elite = False
      contagem = Counter(nomes_monstros)
      descricao_grupo = ', '.join(f'{qtd}x {nome}' for nome, qtd in contagem.items())
      pergunta = (f'{Cor.AMARELO}Você encontrou um grupo: {descricao_grupo}!{Cor.RESET}\n'
                  f'Deseja lutar contra eles?')
    else:
      nomes_monstros = [random.choice(pool)]
      chance_elite = CHANCE_MONSTRO_ELITE
      if nivel_perigo == NIVEL_PERIGO_VERMELHO:
        # área vermelha: monstros "buffados" — a mesma variante elite, só que
        # bem mais frequente.
        chance_elite = max(2, CHANCE_MONSTRO_ELITE // 5)
      elite = random.randint(1, chance_elite) == 1
      prefixo_elite = f'{Cor.AMARELO}[ELITE] {Cor.RESET}' if elite else ''
      pergunta = (f'{Cor.AMARELO}Você encontrou um {prefixo_elite}{nomes_monstros[0]}!{Cor.RESET}\n'
                  f'Deseja lutar contra ele?')

    if ler_confirmacao(pergunta):
      alvo = nomes_monstros if eh_grupo else nomes_monstros[0]
      _lutar(personagem, dungeon_id, alvo, escrever, ler_acao_batalha, aguardar, elite=elite)
    return

  limite_moeda = 3 if nivel_perigo == NIVEL_PERIGO_VERDE else 2
  if random.randint(1, limite_moeda) <= limite_moeda - 1:
    moedas = random.randint(5, 15 + andar.numero * 5)
    personagem.moeda_cobre += moedas
    escrever(f'{Cor.VERDE}Você encontrou {moedas} cobres!{Cor.RESET}')
  else:
    escrever(f'{Cor.CINZA}Você explorou a dungeon e não encontrou nada.{Cor.RESET}')


def _lutar(personagem, dungeon_id, nomes_monstros, escrever, ler_acao_batalha, aguardar, elite=False):
  """`nomes_monstros` é um nome só (chefe, sempre solo) ou uma lista (grupo
  comum) — o formato de saída de `batalhar` acompanha o de entrada."""
  eh_grupo = isinstance(nomes_monstros, list)
  bases = [MONSTROS[nome] for nome in nomes_monstros] if eh_grupo else MONSTROS[nomes_monstros]
  resultado, monstros = batalhar(personagem, bases, escrever=escrever,
                                  ler_acao=ler_acao_batalha, aguardar=aguardar, elite=elite)
  personagem.local = f'dungeon:{dungeon_id}'
  lista = monstros if eh_grupo else [monstros]

  if resultado == ResultadoBatalha.VITORIA:
    for m in lista:
      if not m.vivo:  # só recompensa quem morreu de verdade — quem fugiu, não
        escrever(f'{Cor.VERDE}Você derrotou {m.nome}!{Cor.RESET}')
        conceder_recompensas(personagem, m.base, escrever, elite=m.elite)
  elif resultado == ResultadoBatalha.DERROTA:
    verificar_morte(personagem, escrever)
  elif resultado == ResultadoBatalha.MONSTRO_FUGIU:
    escrever(f'{Cor.CIANO}{lista[0].nome} fugiu — nenhuma recompensa dessa vez.{Cor.RESET}')
