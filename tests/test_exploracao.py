"""Testes de regressão pros níveis de perigo (verde/amarelo/vermelho) dos
pontos de interesse de um andar — calculados pela distância até a entrada,
sem precisar de nenhum dado extra por mapa."""

import random

from rpg.config import (CHANCE_MONSTRO_ELITE, NIVEL_PERIGO_AMARELO, NIVEL_PERIGO_VERDE,
                         NIVEL_PERIGO_VERMELHO)
from rpg.dados.dungeons import DUNGEONS
from rpg.dados.mapas import MAPAS
from rpg.modelos.personagem import Personagem
from rpg.sistemas import exploracao


def _andar_habusken_1():
  return DUNGEONS['habusken'].andares[0]  # comuns: Slime, Slime, Slime, Kobold, Kobold, Lobo


def _personagem():
  return Personagem(nome='teste', classe='Cavaleiro', raca='Humano')


def test_niveis_de_perigo_tem_as_3_cores_e_bate_com_a_distancia():
  mapa = MAPAS['habusken'][1]
  niveis = exploracao._calcular_niveis_perigo(mapa)

  assert set(niveis.values()) == {NIVEL_PERIGO_VERDE, NIVEL_PERIGO_AMARELO, NIVEL_PERIGO_VERMELHO}

  entrada = tuple(exploracao._encontrar_entrada(mapa))
  pontos_verdes = [p for p, n in niveis.items() if n == NIVEL_PERIGO_VERDE]
  pontos_vermelhos = [p for p, n in niveis.items() if n == NIVEL_PERIGO_VERMELHO]
  distancia = lambda p: abs(p[0] - entrada[0]) + abs(p[1] - entrada[1])
  # todo ponto verde tem que estar mais perto da entrada que todo ponto vermelho
  assert max(distancia(p) for p in pontos_verdes) <= min(distancia(p) for p in pontos_vermelhos)


def test_area_verde_prefere_monstros_do_inicio_da_lista(monkeypatch):
  personagem = _personagem()
  andar = _andar_habusken_1()  # ['Slime', 'Slime', 'Slime', 'Kobold', 'Kobold', 'Lobo']

  # sequência: rolagem de chefe falha (2), rolagem de monstro comum acerta (1),
  # rolagem de grupo não acerta (2), rolagem de elite não acerta (2) — só nos
  # importa o pool visto pelo choice.
  sequencia = iter([2, 1, 2, 2])
  monkeypatch.setattr(exploracao.random, 'randint', lambda a, b: next(sequencia))
  pools_vistos = []
  escolha_original = random.choice
  monkeypatch.setattr(exploracao.random, 'choice',
                      lambda pool: pools_vistos.append(list(pool)) or escolha_original(pool))

  exploracao._resolver_evento(personagem, 'habusken', andar, lambda *_a, **_k: None,
                               lambda *_a, **_k: False, None, lambda: None,
                               nivel_perigo=NIVEL_PERIGO_VERDE)

  assert pools_vistos
  assert 'Lobo' not in pools_vistos[0]  # metade final da lista, não devia aparecer na área verde


def test_area_vermelha_prefere_monstros_do_fim_da_lista(monkeypatch):
  personagem = _personagem()
  andar = _andar_habusken_1()

  sequencia = iter([2, 1, 2, 2])
  monkeypatch.setattr(exploracao.random, 'randint', lambda a, b: next(sequencia))
  pools_vistos = []
  escolha_original = random.choice
  monkeypatch.setattr(exploracao.random, 'choice',
                      lambda pool: pools_vistos.append(list(pool)) or escolha_original(pool))

  exploracao._resolver_evento(personagem, 'habusken', andar, lambda *_a, **_k: None,
                               lambda *_a, **_k: False, None, lambda: None,
                               nivel_perigo=NIVEL_PERIGO_VERMELHO)

  assert pools_vistos
  assert 'Slime' not in pools_vistos[0]  # metade inicial da lista, não devia aparecer na área vermelha


def test_area_vermelha_aumenta_chance_de_elite():
  personagem = _personagem()
  andar = _andar_habusken_1()

  random.seed(1)
  elites_vermelho = 0
  for _ in range(200):
    encontrados = []
    exploracao._resolver_evento(
        personagem, 'habusken', andar, lambda *_a, **_k: None,
        lambda p: encontrados.append(p) or False, None, lambda: None,
        nivel_perigo=NIVEL_PERIGO_VERMELHO)
    if encontrados and '[ELITE]' in encontrados[0]:
      elites_vermelho += 1

  elites_padrao = 0
  for _ in range(200):
    encontrados = []
    exploracao._resolver_evento(
        personagem, 'habusken', andar, lambda *_a, **_k: None,
        lambda p: encontrados.append(p) or False, None, lambda: None,
        nivel_perigo=None)
    if encontrados and '[ELITE]' in encontrados[0]:
      elites_padrao += 1

  assert elites_vermelho > elites_padrao


def test_sem_nivel_de_perigo_comporta_se_como_antes():
  """`nivel_perigo=None` (usado pelos testes que chamam `_resolver_evento`
  direto) precisa continuar com o comportamento padrão, sem nenhum viés."""
  personagem = _personagem()
  andar = _andar_habusken_1()
  # não deveria lançar exceção nem se comportar de forma diferente do padrão
  for _ in range(20):
    exploracao._resolver_evento(personagem, 'habusken', andar, lambda *_a, **_k: None,
                                 lambda *_a, **_k: False, None, lambda: None)
  assert personagem.vida >= 0


def test_grupo_de_monstros_nunca_inclui_o_chefe(monkeypatch):
  """Encontro de grupo só pode vir do pool de monstros comuns do andar —
  nunca o chefe (regra explícita: chefe é sempre solo)."""
  personagem = _personagem()
  andar = _andar_habusken_1()
  # sequência: chefe falha, monstro comum acerta, grupo acerta (1), tamanho
  # do grupo = 3 (randint tamanho_min,tamanho_max).
  sequencia = iter([2, 1, 1, 3])
  monkeypatch.setattr(exploracao.random, 'randint', lambda a, b: next(sequencia))
  perguntas = []

  exploracao._resolver_evento(personagem, 'habusken', andar, lambda *_a, **_k: None,
                               lambda p: perguntas.append(p) or False, None, lambda: None,
                               nivel_perigo=None)

  assert perguntas
  assert 'grupo' in perguntas[0].lower()
  assert andar.chefe not in perguntas[0]


def test_lutar_com_lista_de_nomes_gera_batalha_em_grupo(monkeypatch):
  from rpg.dados.classes import CLASSES
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.habilidades_equipadas = list(CLASSES['Cavaleiro'].habilidades_iniciais)
  personagem.poder = 500

  exploracao._lutar(personagem, 'habusken', ['Slime', 'Kobold'], lambda *_a, **_k: None,
                     lambda titulo, opcoes, **kw: 0, lambda: None)

  assert personagem.monstros_derrotados == 2  # os dois do grupo contam


def test_mapa_do_tesouro_reduz_chance_de_achar_chefe_e_e_consumido(monkeypatch):
  personagem = _personagem()
  personagem.itens_ativados = [{'tipo': 'boss_mapa', 'valor': 1}]
  andar = _andar_habusken_1()
  chances_vistas = []
  mensagens = []

  def randint_fake(a, b):
    chances_vistas.append(b)
    return 2  # nunca bate no chefe (2 != 1), mesmo se b for maior que 1

  monkeypatch.setattr(exploracao.random, 'randint', randint_fake)
  exploracao._resolver_evento(personagem, 'habusken', andar, mensagens.append,
                               lambda *_a, **_k: False, None, lambda: None)

  assert chances_vistas[0] == 1  # min(chance_boss original, valor do mapa)
  assert not personagem.itens_ativados  # item usado uma vez e consumido
  assert any('Mapa do Tesouro' in m for m in mensagens)
