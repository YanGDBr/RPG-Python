"""Valida a geometria de todo mapa de exploração: linhas alinhadas, uma
entrada só, e todo ponto de interesse alcançável a pé a partir da entrada —
sem isso, um andar poderia ter uma salinha isolada por engano, inacessível."""

from collections import deque

from rpg.dados.mapas import MAPAS


def _pontos_alcancaveis(mapa):
  altura = len(mapa)
  largura = len(mapa[0])
  inicio = None
  for y, linha in enumerate(mapa):
    for x, celula in enumerate(linha):
      if celula == 'E':
        inicio = (y, x)
  assert inicio is not None, 'mapa sem entrada (E)'

  visitados = {inicio}
  fila = deque([inicio])
  while fila:
    y, x = fila.popleft()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
      ny, nx = y + dy, x + dx
      if not (0 <= ny < altura and 0 <= nx < largura):
        continue
      if (ny, nx) in visitados:
        continue
      if mapa[ny][nx] in ('.', '?', 'E'):
        visitados.add((ny, nx))
        fila.append((ny, nx))
  return visitados


def test_todos_os_mapas_tem_linhas_do_mesmo_tamanho():
  for dungeon_id, andares in MAPAS.items():
    for numero, mapa in andares.items():
      larguras = {len(linha) for linha in mapa}
      assert len(larguras) == 1, f'{dungeon_id} andar {numero}: linhas de tamanho diferente'


def test_todos_os_mapas_tem_exatamente_uma_entrada():
  for dungeon_id, andares in MAPAS.items():
    for numero, mapa in andares.items():
      total_entradas = sum(linha.count('E') for linha in mapa)
      assert total_entradas == 1, f'{dungeon_id} andar {numero}: {total_entradas} entradas (esperado 1)'


def test_todo_ponto_de_interesse_e_alcancavel_a_partir_da_entrada():
  for dungeon_id, andares in MAPAS.items():
    for numero, mapa in andares.items():
      alcancaveis = _pontos_alcancaveis(mapa)
      pontos_de_interesse = [(y, x) for y, linha in enumerate(mapa)
                              for x, c in enumerate(linha) if c == '?']
      assert pontos_de_interesse, f'{dungeon_id} andar {numero}: nenhum ponto de interesse'
      inacessiveis = [p for p in pontos_de_interesse if p not in alcancaveis]
      assert not inacessiveis, f'{dungeon_id} andar {numero}: pontos inacessíveis {inacessiveis}'
