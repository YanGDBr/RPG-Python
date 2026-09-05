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
  # rolagem de elite não acerta (2) — só nos importa o pool visto pelo choice.
  sequencia = iter([2, 1, 2])
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

  sequencia = iter([2, 1, 2])
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
