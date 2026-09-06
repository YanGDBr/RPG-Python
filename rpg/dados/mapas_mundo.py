"""Mapas do mundo aberto (fora de dungeon): a estrada que liga Habusken a
Vethgard e à Cratera de Vhalos, e o vilarejo de Vethgard em si.

Bem diferentes das "salinhas" de antes: aqui o mapa é um campo aberto grande
de verdade (bem maior que a tela — ver JANELA_MUNDO_* em config.py, a câmera
que rola em rpg/sistemas/mundo.py), com florestas, baús e itens largados pelo
chão, além dos NPCs e pontos de viagem. Continua tudo fixo (nunca
procedural) — só que em vez de desenhar caractere por caractere, cada mapa é
descrito por coordenada (`_construir_mapa_aberto`), o que é bem menos
propenso a erro de digitação num campo desse tamanho.

Convenção de caractere: '.' é andável, 'E' é a entrada, qualquer letra/dígito
registrado em `eventos` (ver rpg/jogo.py) é andável e abre alguma coisa
(diálogo, baú, item, viagem), 'F' é floresta (andável, com chance de monstro
selvagem) e qualquer outro caractere é parede/obstáculo (árvore, pedra etc.).
"""


def _construir_mapa_aberto(largura, altura, entrada, obstaculos=(), floresta=(), pontos=None,
                            parede='#'):
  grade = [['.' for _ in range(largura)] for _ in range(altura)]
  for x in range(largura):
    grade[0][x] = parede
    grade[altura - 1][x] = parede
  for y in range(altura):
    grade[y][0] = parede
    grade[y][largura - 1] = parede
  for y, x in obstaculos:
    grade[y][x] = parede
  for y, x in floresta:
    grade[y][x] = 'F'
  for (y, x), caractere in (pontos or {}).items():
    grade[y][x] = caractere
  ey, ex = entrada
  grade[ey][ex] = 'E'
  return tuple(''.join(linha) for linha in grade)


def _bloco(y0, x0, y1, x1):
  """Todas as coordenadas de um retângulo (inclusive nas duas pontas) —
  atalho pra declarar um pequeno aglomerado de árvores/pedras ou uma moita de
  floresta sem listar coordenada por coordenada."""
  return [(y, x) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]


# --------------------------------------------------------- Estrada (Ilyrath)
# Liga a Vila Habusken (entrada, lado esquerdo) a Vethgard ('V', lado
# direito) e à Cratera de Vhalos ('C', ramo ao norte — bloqueado até se ter o
# Selo de Vethgard). 'T' é o Velho Caminhante, 'S' é a Arquivista Sorel e 'M'
# é o Órfão Mikel — os dois últimos ficavam dentro de Vethgard, mas a
# recompensa das sidequests deles é baixa demais pro nível que se chega lá
# (só depois de zerar a dungeon de Habusken inteira) — fazem mais sentido
# aqui, ainda no início da estrada. '1'/'2' são baús, '3'/'4'/'5' são itens
# largados no chão.
ILYRATH_OBSTACULOS = (
    _bloco(7, 14, 8, 15) + _bloco(13, 17, 14, 18) + _bloco(6, 25, 7, 25)
    + _bloco(3, 22, 3, 24))
ILYRATH_FLORESTA = _bloco(4, 18, 6, 19) + _bloco(10, 28, 12, 29)
ILYRATH_PONTOS = {
  (9, 8): 'T',    # Velho Caminhante
  (5, 5): 'S',    # Arquivista Sorel (sidequest)
  (15, 30): 'M',  # Órfão Mikel (sidequest)
  (4, 12): '1',   # baú
  (13, 22): '2',  # baú
  (14, 11): '3',  # item: material
  (16, 24): '4',  # item: Lenço da Família de Mikel (sidequest)
  (4, 30): '5',   # item: moedas
  (2, 34): 'C',   # ramo norte -> Cratera de Vhalos
  (9, 38): 'V',   # -> Vethgard
}
MAPA_ILYRATH = _construir_mapa_aberto(
    largura=41, altura=19, entrada=(9, 1),
    obstaculos=ILYRATH_OBSTACULOS, floresta=ILYRATH_FLORESTA, pontos=ILYRATH_PONTOS)


# ------------------------------------------------------------------ Vethgard
# Segunda cidade de verdade (não só um punhado de NPCs): tem sua própria loja
# ('L', acessórios mais fortes), curandeira ('C'), mestre de treinamento
# ('T', concede Disciplina em vez de Etén), e é daqui que se entra na Torre
# Arcana ('A') e no Abismo Submerso ('B') — as duas dungeons "do meio do
# jogo" saíram do menu de Habusken pra cá, fazendo mais sentido narrativo.
# 'W' é a Capitã Wren e 'R' o Estudioso Aldric (sidequests de recompensa bem
# maior — só se chega em Vethgard depois de zerar Habusken inteira). 'G'
# continua sendo o Guarda de Vethgard (só diálogo). '6' é um baú.
# Sair (Esc) devolve o jogador ao mapa de Ilyrath.
VETHGARD_OBSTACULOS = _bloco(6, 13, 7, 14) + _bloco(10, 24, 11, 25) + _bloco(3, 26, 4, 26)
VETHGARD_PONTOS = {
  (8, 4): 'G',    # Guarda de Vethgard
  (4, 10): 'L',   # Loja de Vethgard
  (12, 10): 'C',  # Curandeira
  (4, 20): 'T',   # Mestre de Vethgard
  (8, 16): 'W',   # Capitã Wren (sidequest)
  (12, 22): 'R',  # Estudioso Aldric (sidequest)
  (2, 30): 'A',   # -> Torre Arcana
  (14, 30): 'B',  # -> Abismo Submerso
  (4, 30): '6',   # baú
}
MAPA_VETHGARD = _construir_mapa_aberto(
    largura=37, altura=17, entrada=(8, 1),
    obstaculos=VETHGARD_OBSTACULOS, pontos=VETHGARD_PONTOS)
