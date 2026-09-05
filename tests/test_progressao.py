"""Testes de regressão para a morte (sem tempo de espera, com punição
instantânea) e para o multiplicador global de experiência."""

from math import trunc

from rpg.config import ACOES_POR_DESGASTE_FOME, MULTIPLICADOR_EXP_GLOBAL
from rpg.dados.monstros import MONSTROS
from rpg.modelos.personagem import Personagem
from rpg.sistemas import progressao


def _personagem():
  p = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  p.nivel = 5
  p.moeda_cobre = 1000
  p.moeda_prata = 40
  p.moeda_ouro = 4
  p.vida = 0
  return p


def test_morrer_nao_espera_e_ja_volta_de_pe():
  personagem = _personagem()
  mensagens = []

  morreu = progressao.verificar_morte(personagem, mensagens.append)

  assert morreu is True
  assert personagem.vida == 10
  assert personagem.mana == 10
  assert personagem.fome == 1


def test_morrer_perde_um_nivel_e_zera_exp_do_nivel():
  personagem = _personagem()
  personagem.exp = 30

  progressao.verificar_morte(personagem, lambda *_a, **_k: None)

  assert personagem.nivel == 4
  assert personagem.exp == 0
  assert personagem.exp_para_subir == 4 * 50


def test_morrer_no_nivel_1_nao_fica_negativo():
  personagem = _personagem()
  personagem.nivel = 1

  progressao.verificar_morte(personagem, lambda *_a, **_k: None)

  assert personagem.nivel == 1


def test_morrer_perde_metade_de_todas_as_moedas():
  personagem = _personagem()

  progressao.verificar_morte(personagem, lambda *_a, **_k: None)

  assert personagem.moeda_cobre == 500
  assert personagem.moeda_prata == 20
  assert personagem.moeda_ouro == 2


def test_morte_nao_reproduz_se_vida_ainda_positiva():
  personagem = _personagem()
  personagem.vida = 1

  assert progressao.verificar_morte(personagem, lambda *_a, **_k: None) is False


def test_exp_de_monstro_e_multiplicada_pelo_multiplicador_global(monkeypatch):
  personagem = _personagem()
  personagem.vida = personagem.vida_maxima
  personagem.exp_para_subir = 100_000  # garante que não sobe de nível no meio do teste
  monstro = MONSTROS['Kobold']

  monkeypatch.setattr(progressao.random, 'randint', lambda minimo, _maximo: minimo)

  progressao.conceder_recompensas(personagem, monstro, lambda *_a, **_k: None)

  assert personagem.exp == trunc(monstro.exp_min * MULTIPLICADOR_EXP_GLOBAL)


def test_fome_so_desgasta_a_cada_n_acoes():
  personagem = _personagem()
  personagem.vida = personagem.vida_maxima
  personagem.fome = 10

  for _ in range(ACOES_POR_DESGASTE_FOME - 1):
    progressao.aplicar_desgaste_fome(personagem, lambda *_a, **_k: None)
  assert personagem.fome == 10  # ainda não completou o ciclo

  progressao.aplicar_desgaste_fome(personagem, lambda *_a, **_k: None)
  assert personagem.fome == 9  # completou o ciclo, desgasta 1
  assert personagem.acoes_desde_desgaste_fome == 0
