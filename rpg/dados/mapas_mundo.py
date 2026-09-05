"""Mapas do mundo aberto (fora de dungeon): a estrada que liga Habusken a
Vethgard e à Cratera de Vhalos, e o vilarejo de Vethgard em si. Os pontos de
interesse aqui abrem diálogo ou viagem — nunca batalha (ver rpg/sistemas/mundo.py).

Mesma convenção de caractere das dungeons ('.' andável, 'E' entrada, parede é
qualquer outro caractere), com uma diferença: em vez de um único `?` genérico
pra "algo pode acontecer aqui", cada ponto de interesse tem seu próprio
caractere, porque cada um é um NPC ou destino específico, não um sorteio.
"""


def _construir_mapa_estrada(largura, altura, ramos, parede, entrada_coluna=1):
  """Mesma forma do `_construir_mapa_pente` de mapas.py (espinha central com
  ramos alternando pra cima e pra baixo) — só que `ramos` é uma lista de
  (coluna, caractere), pra cada ramo terminar num ponto de interesse
  diferente em vez de um `?` uniforme."""
  espinha = altura // 2
  grade = [[parede] * largura for _ in range(altura)]
  for x in range(1, largura - 1):
    grade[espinha][x] = '.'
  for i, (coluna, caractere) in enumerate(ramos):
    se_for_par_sobe = i % 2 == 0
    if se_for_par_sobe:
      for y in range(1, espinha):
        grade[y][coluna] = '.'
      grade[1][coluna] = caractere
    else:
      for y in range(espinha + 1, altura - 1):
        grade[y][coluna] = '.'
      grade[altura - 2][coluna] = caractere
  grade[espinha][entrada_coluna] = 'E'
  return tuple(''.join(linha) for linha in grade)


# 'T' = Velho Caminhante (NPC) — 'V' = viajar para Vethgard — 'C' = viajar
# para a Cratera de Vhalos (bloqueado até derrotar o Kraken Ancestral).
MAPA_ILYRATH = _construir_mapa_estrada(
    33, 11, ramos=[(6, 'T'), (16, 'V'), (26, 'C')], parede='^', entrada_coluna=1)

# 'S' = Arquivista Sorel — 'M' = Órfão Mikel — 'G' = Guarda de Vethgard.
# Sair (Esc) devolve o jogador ao mapa de Ilyrath.
MAPA_VETHGARD = _construir_mapa_estrada(
    27, 9, ramos=[(5, 'S'), (13, 'M'), (20, 'G')], parede='=', entrada_coluna=1)
