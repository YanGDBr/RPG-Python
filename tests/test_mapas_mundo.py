"""Valida a geometria dos mapas do mundo aberto (estrada de Ilyrath e
Vethgard): linhas alinhadas, uma entrada só, e todo ponto de interesse
(NPC ou destino) alcançável a pé a partir da entrada.

Diferente das dungeons (um `?` genérico), cada mapa do mundo tem seus
próprios caracteres de evento — listados explicitamente aqui, então o teste
sempre sabe distinguir "parede" de "ponto de interesse" sem adivinhar."""

from collections import deque

from rpg.dados.mapas_mundo import MAPA_ILYRATH, MAPA_VETHGARD

MAPAS_MUNDO = {
  'ilyrath': (MAPA_ILYRATH, {'T', 'V', 'C'}),
  'vethgard': (MAPA_VETHGARD, {'S', 'M', 'G'}),
}


def _alcancaveis(mapa, eventos):
  altura, largura = len(mapa), len(mapa[0])
  inicio = None
  for y, linha in enumerate(mapa):
    x = linha.find('E')
    if x != -1:
      inicio = (y, x)
  assert inicio is not None, 'mapa sem entrada (E)'

  celulas_andaveis = {'.', 'E'} | eventos
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
      if mapa[ny][nx] in celulas_andaveis:
        visitados.add((ny, nx))
        fila.append((ny, nx))
  return visitados


def test_mapas_do_mundo_tem_linhas_do_mesmo_tamanho():
  for nome, (mapa, _eventos) in MAPAS_MUNDO.items():
    larguras = {len(linha) for linha in mapa}
    assert len(larguras) == 1, f'{nome}: linhas de tamanho diferente'


def test_mapas_do_mundo_tem_exatamente_uma_entrada():
  for nome, (mapa, _eventos) in MAPAS_MUNDO.items():
    total_entradas = sum(linha.count('E') for linha in mapa)
    assert total_entradas == 1, f'{nome}: {total_entradas} entradas (esperado 1)'


def test_todo_ponto_de_interesse_do_mundo_e_alcancavel():
  for nome, (mapa, eventos) in MAPAS_MUNDO.items():
    alcancaveis = _alcancaveis(mapa, eventos)
    pontos = [(y, x) for y, linha in enumerate(mapa)
              for x, c in enumerate(linha) if c in eventos]
    assert pontos, f'{nome}: nenhum ponto de interesse'
    inacessiveis = [p for p in pontos if p not in alcancaveis]
    assert not inacessiveis, f'{nome}: pontos inacessíveis {inacessiveis}'
