"""Testes de integração ponta a ponta — igual ao smoke test manual que rodei
antes de reestruturar tudo, só que automatizado: como `menu()`/`ler_tecla()`
aceitam leitor/escritor injetáveis, dá pra simular um jogador de verdade sem
precisar de um terminal interativo.
"""

import itertools
import random
from collections import deque

from rpg.dados.classes import CLASSES
from rpg.dados.dungeons import DUNGEONS
from rpg.dados.mapas import MAPAS
from rpg.dados.mapas_mundo import MAPA_ILYRATH, MAPA_VETHGARD
from rpg.dados.monstros import MONSTROS
from rpg.modelos.personagem import Personagem
from rpg.sistemas import batalha, exploracao, loja, mundo, progressao
from rpg.sistemas.exploracao import DESLOCAMENTOS, _encontrar_entrada
from rpg.sistemas.mundo import DESLOCAMENTOS as DESLOCAMENTOS_MUNDO


def _leitor_menu_sequencia(sequencia):
  fila = list(sequencia)

  def _fake(_titulo, _opcoes, **_kwargs):
    return fila.pop(0)

  return _fake


def _personagem_cavaleiro():
  personagem = Personagem(nome='HeroiTeste', classe='Cavaleiro', raca='Humano')
  personagem.habilidades_aprendidas = list(CLASSES['Cavaleiro'].habilidades_iniciais)
  personagem.habilidades_equipadas = list(CLASSES['Cavaleiro'].habilidades_iniciais)
  return personagem


def test_comprar_pocao_de_vida_debita_moedas_e_adiciona_ao_inventario():
  personagem = _personagem_cavaleiro()
  mensagens = []

  loja.loja_pocoes(personagem, escrever=mensagens.append,
                    ler_acao=_leitor_menu_sequencia([0, None]),  # índice 0 = Poção de Vida
                    aguardar=lambda: None)

  assert personagem.pocoes.get('Vida', 0) == 1
  assert personagem.moeda_cobre == 200 - 30
  assert any('Vida' in m for m in mensagens)


def _caminho_ate_ponto_de_interesse(mapa):
  """Faz uma busca em largura da entrada até o '?' mais próximo e devolve a
  sequência exata de direções pra chegar lá — o mapa agora tem paredes de
  verdade, então não dá mais pra "andar em círculo" e confiar que vai
  encontrar alguma coisa em algum momento."""
  inicio = tuple(_encontrar_entrada(mapa))
  visitados = {inicio}
  fila = deque([(inicio, [])])
  while fila:
    (y, x), caminho = fila.popleft()
    if mapa[y][x] == '?':
      return caminho
    for direcao, (dy, dx) in DESLOCAMENTOS.items():
      ny, nx = y + dy, x + dx
      if (ny, nx) in visitados:
        continue
      if not (0 <= ny < len(mapa) and 0 <= nx < len(mapa[0])):
        continue
      if mapa[ny][nx] not in ('.', '?', 'E'):
        continue
      visitados.add((ny, nx))
      fila.append(((ny, nx), caminho + [direcao]))
  raise AssertionError('nenhum ponto de interesse alcançável — mapa quebrado')


def test_explorar_um_andar_e_lutar_ate_vencer():
  random.seed(99)
  personagem = _personagem_cavaleiro()
  personagem.poder = 500
  personagem.andar_atual['habusken'] = 1
  mensagens = []

  mapa = MAPAS['habusken'][1]
  caminho = iter(_caminho_ate_ponto_de_interesse(mapa))

  exploracao.explorar(
      personagem, 'habusken', escrever=mensagens.append,
      leitor_tecla=lambda: next(caminho),
      limpar=lambda: None,
      ler_confirmacao=lambda *_a, **_k: True,
      ler_acao_batalha=lambda _titulo, _opcoes, **_kw: 0,  # sempre usa a 1ª habilidade
      aguardar=lambda: None)

  # Não importa qual dos 3 eventos aconteceu (monstro, moedas ou nada) — o
  # personagem tem que continuar num estado consistente e sem exceções.
  assert personagem.vida >= 0
  assert personagem.fome == 9  # aplicar_desgaste_fome rodou (começa em 10)


def test_monstro_da_missao_tem_mais_chance_de_aparecer_na_exploracao(monkeypatch):
  """A guilda dá uma missão pra matar um monstro específico do andar — sem
  favorecer esse monstro na exploração, encontrá-lo era pura sorte igual aos
  outros, e a missão quase nunca avançava."""
  personagem = _personagem_cavaleiro()
  andar = DUNGEONS['habusken'].andares[0]  # comuns: 3x Slime, 2x Kobold, 1x Lobo
  personagem.missoes_ativas = [{'monstro': 'Lobo', 'quantidade_atual': 0, 'quantidade_alvo': 3}]  # o mais raro naturalmente (1 em 6)

  # 1º randint de cada chamada = checagem de chefe (qualquer valor != 1 evita);
  # 2º = checagem de "achou monstro comum" (valor <= peso_monstro dispara).
  sequencia = itertools.cycle([2, 1])
  monkeypatch.setattr(exploracao.random, 'randint', lambda a, b: next(sequencia))

  encontrados = []

  def _confirmar(pergunta):
    encontrados.append(pergunta)
    return False

  for _ in range(300):
    exploracao._resolver_evento(personagem, 'habusken', andar, lambda *_a, **_k: None,
                                 _confirmar, None, lambda: None)

  proporcao_lobo = sum(1 for p in encontrados if 'Lobo' in p) / len(encontrados)
  assert proporcao_lobo > 1 / 6


def _caminho_ate_evento(mapa, eventos, alvo):
  """Mesma ideia de `_caminho_ate_ponto_de_interesse`, adaptada pro mundo
  aberto: BFS da entrada até um caractere de evento específico (em vez do
  `?` genérico das dungeons)."""
  inicio = tuple(_encontrar_entrada(mapa))
  celulas_andaveis = {'.', 'E'} | set(eventos)
  visitados = {inicio}
  fila = deque([(inicio, [])])
  while fila:
    (y, x), caminho = fila.popleft()
    if mapa[y][x] == alvo:
      return caminho
    for direcao, (dy, dx) in DESLOCAMENTOS_MUNDO.items():
      ny, nx = y + dy, x + dx
      if (ny, nx) in visitados:
        continue
      if not (0 <= ny < len(mapa) and 0 <= nx < len(mapa[0])):
        continue
      if mapa[ny][nx] not in celulas_andaveis:
        continue
      visitados.add((ny, nx))
      fila.append(((ny, nx), caminho + [direcao]))
  raise AssertionError(f'"{alvo}" inalcançável — mapa do mundo quebrado')


def test_mundo_aberto_bloqueia_cratera_e_permite_visitar_vethgard():
  """Simula um jogador andando pelo mapa de Ilyrath de verdade: tenta entrar
  na Cratera de Vhalos antes de liberar (deve ser barrado), depois viaja até
  Vethgard e conversa com um NPC de lá."""
  personagem = Personagem(nome='HeroiTeste', classe='Cavaleiro', raca='Humano')
  mensagens = []

  eventos_ilyrath = {
    'T': mundo.falar_com_npc('velho_caminhante'),
    'V': lambda p, e, a, l: 'vethgard',
    'C': lambda p, e, a, l: 'cratera' if p.cratera_vhalos_liberado else None,
  }

  caminho_cratera = iter(_caminho_ate_evento(MAPA_ILYRATH, eventos_ilyrath, 'C') + ['esc'])
  resultado = mundo.explorar_mapa(
      personagem, MAPA_ILYRATH, eventos_ilyrath, 'Mapa de Ilyrath',
      escrever=mensagens.append, leitor_tecla=lambda: next(caminho_cratera),
      limpar=lambda: None, aguardar=lambda: None)
  assert resultado is None  # barrado (cratera_vhalos_liberado ainda é False)

  caminho_vethgard = iter(_caminho_ate_evento(MAPA_ILYRATH, eventos_ilyrath, 'V'))
  resultado = mundo.explorar_mapa(
      personagem, MAPA_ILYRATH, eventos_ilyrath, 'Mapa de Ilyrath',
      escrever=mensagens.append, leitor_tecla=lambda: next(caminho_vethgard),
      limpar=lambda: None, aguardar=lambda: None)
  assert resultado == 'vethgard'

  eventos_vethgard = {'S': mundo.falar_com_npc('arquivista_sorel'),
                       'M': mundo.falar_com_npc('orfao_mikel'),
                       'G': mundo.falar_com_npc('guarda_vethgard')}
  caminho_sorel = iter(_caminho_ate_evento(MAPA_VETHGARD, eventos_vethgard, 'S') + ['esc'])
  mundo.explorar_mapa(
      personagem, MAPA_VETHGARD, eventos_vethgard, 'Vethgard',
      escrever=mensagens.append, leitor_tecla=lambda: next(caminho_sorel),
      limpar=lambda: None, aguardar=lambda: None)

  assert any('Arquivista Sorel' in m for m in mensagens)


def test_vitoria_concede_recompensas_e_possivelmente_sobe_de_nivel():
  random.seed(5)
  personagem = _personagem_cavaleiro()
  personagem.poder = 500
  mensagens = []

  resultado, monstro = batalha.batalhar(
      personagem, MONSTROS['Kobold'], escrever=mensagens.append,
      ler_acao=lambda titulo, opcoes, **kw: 0, aguardar=lambda: None)
  assert resultado == batalha.ResultadoBatalha.VITORIA

  exp_antes = personagem.exp
  progressao.conceder_recompensas(personagem, monstro.base, mensagens.append)
  assert personagem.moeda_cobre >= 200  # ganhou moedas em cima do saldo inicial
  assert personagem.exp != exp_antes or personagem.nivel > 1
