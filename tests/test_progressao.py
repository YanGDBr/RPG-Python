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


def test_derrotar_chefe_de_habusken_concede_selo_de_identidade(monkeypatch):
  personagem = _personagem()
  personagem.vida = personagem.vida_maxima
  monstro = MONSTROS['Dragão Ancião de Habusken']
  monkeypatch.setattr(progressao.random, 'randint', lambda minimo, _maximo: minimo)

  progressao.conceder_recompensas(personagem, monstro, lambda *_a, **_k: None)

  assert personagem.itens_especiais.get('Selo de Habusken') == 1


def test_primeiro_abate_de_chefe_concede_bonus_de_recompensa(monkeypatch):
  """Pedido explícito do usuário: a primeira vez que se derrota um chefe
  específico dá uma recompensa turbinada, além do já aumentado normal.
  Usa `moedas_totais_ganhas` (não `exp`) pra comparar, já que `exp` passa
  por level-up e o excedente vira resto — moedas é uma soma direta, sem
  esse efeito colateral."""
  from rpg.config import BONUS_PRIMEIRO_ABATE_CHEFE_PERCENTUAL
  personagem = _personagem()
  personagem.vida = personagem.vida_maxima
  monstro = MONSTROS['Slime Gigante']
  monkeypatch.setattr(progressao.random, 'randint', lambda minimo, _maximo: minimo)
  monkeypatch.setattr(progressao.random, 'random', lambda: 1.0)  # nenhum drop de item aleatório

  progressao.conceder_recompensas(personagem, monstro, lambda *_a, **_k: None)

  moedas_esperadas = trunc(monstro.moedas_min + monstro.moedas_min * BONUS_PRIMEIRO_ABATE_CHEFE_PERCENTUAL / 100)
  assert personagem.moedas_totais_ganhas == moedas_esperadas
  assert personagem.moeda_cobre == 1000 + moedas_esperadas


def test_segundo_abate_do_mesmo_chefe_nao_repete_o_bonus(monkeypatch):
  personagem = _personagem()
  personagem.vida = personagem.vida_maxima
  monstro = MONSTROS['Slime Gigante']
  personagem.chefes_derrotados.append(monstro.nome)  # já derrotado antes
  monkeypatch.setattr(progressao.random, 'randint', lambda minimo, _maximo: minimo)
  monkeypatch.setattr(progressao.random, 'random', lambda: 1.0)

  progressao.conceder_recompensas(personagem, monstro, lambda *_a, **_k: None)

  assert personagem.moedas_totais_ganhas == monstro.moedas_min  # sem bônus de "primeira vez"


def test_derrotar_chefe_sem_documento_nao_ganha_item_especial(monkeypatch):
  personagem = _personagem()
  personagem.vida = personagem.vida_maxima
  monstro = MONSTROS['Kobold']  # não é chefe
  monkeypatch.setattr(progressao.random, 'randint', lambda minimo, _maximo: minimo)

  progressao.conceder_recompensas(personagem, monstro, lambda *_a, **_k: None)

  assert personagem.itens_especiais == {}


def test_derrotar_monstro_avanca_sidequest_de_derrotar_ativa(monkeypatch):
  personagem = _personagem()
  personagem.vida = personagem.vida_maxima
  personagem.sidequests_ativas = [{'id': 'ecos_da_cantiga', 'progresso': 0}]
  monstro = MONSTROS['Lobo']
  monkeypatch.setattr(progressao.random, 'randint', lambda minimo, _maximo: minimo)

  progressao.conceder_recompensas(personagem, monstro, lambda *_a, **_k: None)

  assert personagem.sidequests_ativas[0]['progresso'] == 1


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


def test_aplicar_desgaste_fome_aceita_limite_de_acoes_customizado():
  """O mundo aberto passa um limiar bem maior (ACOES_POR_DESGASTE_FOME_MUNDO)
  que o padrão de dungeon, já que lá desgasta por passo de verdade."""
  personagem = _personagem()
  personagem.vida = personagem.vida_maxima
  personagem.fome = 10

  progressao.aplicar_desgaste_fome(personagem, lambda *_a, **_k: None, limite_acoes=5)
  assert personagem.fome == 10  # ainda não completou o ciclo de 5

  for _ in range(4):
    progressao.aplicar_desgaste_fome(personagem, lambda *_a, **_k: None, limite_acoes=5)
  assert personagem.fome == 9


def test_fome_zerada_nunca_derruba_a_vida_abaixo_de_um():
  """Pedido explícito do usuário: não dá pra morrer de fome, só ficar no
  mínimo com 1 de vida."""
  personagem = _personagem()
  personagem.fome = 0
  personagem.vida = 3

  for _ in range(ACOES_POR_DESGASTE_FOME):
    progressao.aplicar_desgaste_fome(personagem, lambda *_a, **_k: None)

  assert personagem.vida == 1

  for _ in range(ACOES_POR_DESGASTE_FOME):
    progressao.aplicar_desgaste_fome(personagem, lambda *_a, **_k: None)

  assert personagem.vida == 1  # continua no mínimo, nunca some pra 0
