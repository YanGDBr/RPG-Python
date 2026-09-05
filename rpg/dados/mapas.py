"""Mapas de exploração — um layout próprio por andar, no lugar da grade
genérica de pontinhos que existia antes.

Cada mapa é uma tupla de strings (todas do mesmo tamanho). Convenção de
caracteres: '.' é chão andável, '?' é um ponto de interesse (onde um evento de
exploração pode acontecer — monstro, chefe, moedas ou nada, do mesmo jeito que
já funcionava), 'E' é a entrada (onde o personagem começa a andar) e qualquer
outro caractere é parede (bloqueia passagem). Isso deixa o desenho do mapa
livre pra qualquer forma, sem precisar mexer no motor de exploração.

Os três `_construir_mapa_*` são pequenos "moldes" que montam um layout válido
e conectado a partir de alguns parâmetros — usados pra gerar 8 mapas com
formas bem diferentes entre si (corredor com ramos, dupla espinha com salas
nas pontas, salão central com corredores radiais) sem correr o risco de
desalinhar um mapa digitado à mão character por character.
"""

import math


def _construir_mapa_pente(largura, altura, ramos, parede, entrada_coluna=1):
  """Um corredor central (a "espinha"), com ramos alternando pra cima e pra
  baixo, cada um terminando numa salinha (?)."""
  espinha = altura // 2
  grade = [[parede] * largura for _ in range(altura)]
  for x in range(1, largura - 1):
    grade[espinha][x] = '.'
  for i, coluna in enumerate(ramos):
    se_for_par_sobe = i % 2 == 0
    if se_for_par_sobe:
      for y in range(1, espinha):
        grade[y][coluna] = '.'
      grade[1][coluna] = '?'
    else:
      for y in range(espinha + 1, altura - 1):
        grade[y][coluna] = '.'
      grade[altura - 2][coluna] = '?'
  grade[espinha][entrada_coluna] = 'E'
  return tuple(''.join(linha) for linha in grade)


def _construir_mapa_grade(largura, altura, linha_superior, linha_inferior,
                           ligacoes, parede, entrada_coluna=1):
  """Duas espinhas horizontais (em cima e embaixo), cada uma com uma salinha
  em cada ponta, conectadas por alguns corredores verticais."""
  grade = [[parede] * largura for _ in range(altura)]
  for x in range(1, largura - 1):
    grade[linha_superior][x] = '.'
    grade[linha_inferior][x] = '.'
  grade[linha_superior][1] = '?'
  grade[linha_superior][largura - 2] = '?'
  grade[linha_inferior][1] = '?'
  grade[linha_inferior][largura - 2] = '?'
  for coluna in ligacoes:
    for y in range(linha_superior + 1, linha_inferior):
      grade[y][coluna] = '.'
  grade[linha_superior][entrada_coluna] = 'E'
  return tuple(''.join(linha) for linha in grade)


def _construir_mapa_salao(largura, altura, raio_sala, parede, pontos_relativos):
  """Um salão em forma de losango no centro, com corredores retos saindo em
  várias direções até salinhas — para os andares de clímax (chefe final)."""
  centro_y, centro_x = altura // 2, largura // 2
  grade = [[parede] * largura for _ in range(altura)]
  for y in range(altura):
    for x in range(largura):
      if abs(y - centro_y) + abs(x - centro_x) <= raio_sala:
        grade[y][x] = '.'
  for delta_y, delta_x in pontos_relativos:
    alvo_y = max(1, min(altura - 2, centro_y + delta_y))
    alvo_x = max(1, min(largura - 2, centro_x + delta_x))
    y, x = centro_y, centro_x
    passo_y = 1 if alvo_y > y else -1
    while y != alvo_y:
      y += passo_y
      if grade[y][x] == parede:
        grade[y][x] = '.'
    passo_x = 1 if alvo_x > x else -1
    while x != alvo_x:
      x += passo_x
      if grade[y][x] == parede:
        grade[y][x] = '.'
    grade[alvo_y][alvo_x] = '?'
  grade[centro_y][centro_x] = 'E'
  return tuple(''.join(linha) for linha in grade)


MAPAS = {
  'habusken': {
    1: _construir_mapa_pente(29, 11, ramos=[4, 8, 12, 16, 20, 24],
                              parede='o', entrada_coluna=1),
    2: _construir_mapa_grade(33, 11, linha_superior=2, linha_inferior=8,
                               ligacoes=[6, 16, 26], parede='x', entrada_coluna=1),
    3: _construir_mapa_pente(35, 13, ramos=[4, 9, 14, 19, 24, 29],
                              parede='#', entrada_coluna=17),
    4: _construir_mapa_grade(33, 13, linha_superior=3, linha_inferior=9,
                               ligacoes=[8, 16, 24], parede='+', entrada_coluna=16),
    5: _construir_mapa_salao(37, 17, raio_sala=6, parede='^',
                               pontos_relativos=[(-8, 0), (8, 0), (0, -14), (0, 14),
                                                  (-6, -10), (6, 10)]),
  },
  'torre_arcana': {
    1: _construir_mapa_pente(31, 11, ramos=[4, 8, 12, 16, 20, 24],
                              parede='*', entrada_coluna=29),
    2: _construir_mapa_grade(33, 11, linha_superior=2, linha_inferior=8,
                               ligacoes=[6, 16, 26], parede='%', entrada_coluna=1),
    3: _construir_mapa_salao(39, 19, raio_sala=7, parede='&',
                               pontos_relativos=[(-9, 0), (9, 0), (0, -16), (0, 16),
                                                  (-7, -11), (7, 11), (-7, 11), (7, -11)]),
  },
  'abismo_submerso': {
    1: _construir_mapa_pente(33, 11, ramos=[4, 9, 14, 19, 24, 29],
                              parede='~', entrada_coluna=1),
    2: _construir_mapa_grade(35, 13, linha_superior=3, linha_inferior=9,
                               ligacoes=[7, 17, 27], parede='=', entrada_coluna=17),
    3: _construir_mapa_salao(41, 19, raio_sala=8, parede=':',
                               pontos_relativos=[(-9, 0), (9, 0), (0, -17), (0, 17),
                                                  (-7, -12), (7, 12), (-7, 12), (7, -12)]),
  },
}
