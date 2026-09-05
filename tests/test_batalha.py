import random

from rpg.config import Cor
from rpg.dados.classes import CLASSES
from rpg.dados.monstros import MONSTROS
from rpg.modelos.monstro import MonstroBatalha
from rpg.modelos.personagem import Personagem
from rpg.sistemas import batalha


def _personagem_cavaleiro():
  p = Personagem(nome='teste', senha_hash='x', classe='Cavaleiro', raca='Humano')
  p.habilidades_equipadas = list(CLASSES['Cavaleiro'].habilidades_iniciais)
  return p


def test_multiplicador_elemental_fraqueza_e_resistencia():
  monstro = MonstroBatalha.instanciar(MONSTROS['Slime'])  # fraqueza Fogo, resistência Físico
  assert batalha.multiplicador_elemental('Fogo', monstro) == 1.5
  assert batalha.multiplicador_elemental('Fisico', monstro) == 0.5
  assert batalha.multiplicador_elemental('Eletrico', monstro) == 1.0


def test_calcular_dano_e_sempre_positivo():
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = CLASSES['Cavaleiro'].habilidades_iniciais[0]
  from rpg.dados.habilidades import HABILIDADES
  dano, _critico = batalha.calcular_dano(personagem, HABILIDADES[habilidade], monstro)
  assert dano > 0


def test_fome_critica_reduz_o_dano():
  from rpg.dados.habilidades import HABILIDADES
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = HABILIDADES['Investida']

  personagem_bem_alimentado = _personagem_cavaleiro()
  personagem_bem_alimentado.fome = 10
  random.seed(123)
  dano_normal, _ = batalha.calcular_dano(personagem_bem_alimentado, habilidade, monstro)

  personagem_faminto = _personagem_cavaleiro()
  personagem_faminto.fome = 1
  random.seed(123)
  dano_faminto, _ = batalha.calcular_dano(personagem_faminto, habilidade, monstro)

  assert dano_faminto < dano_normal


def test_batalha_termina_em_vitoria_com_poder_avassalador():
  random.seed(7)
  personagem = _personagem_cavaleiro()
  personagem.poder = 500

  resultado, monstro = batalha.batalhar(
      personagem, MONSTROS['Slime'], escrever=lambda *_a, **_k: None,
      ler_acao=lambda titulo, opcoes, **kw: 0, aguardar=lambda: None)

  assert resultado == batalha.ResultadoBatalha.VITORIA
  assert monstro.vida == 0


def test_batalha_pausa_ao_menos_uma_vez_por_rodada_para_dar_tempo_de_ler():
  """Regressão: as mensagens de dano/efeito apareciam e a tela já limpava
  antes de dar tempo de ler."""
  random.seed(7)
  personagem = _personagem_cavaleiro()
  personagem.poder = 500
  chamadas_aguardar = []

  batalha.batalhar(
      personagem, MONSTROS['Kobold'], escrever=lambda *_a, **_k: None,
      ler_acao=lambda titulo, opcoes, **kw: 0,
      aguardar=lambda: chamadas_aguardar.append(1))

  assert len(chamadas_aguardar) >= 1


def test_mensagem_de_dano_e_colorida_de_vermelho():
  random.seed(1)
  personagem = _personagem_cavaleiro()
  personagem.poder = 10
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  mensagens = []

  from rpg.dados.habilidades import HABILIDADES
  batalha.personagem_ataca(personagem, HABILIDADES['Investida'], monstro, mensagens.append)

  assert any(Cor.VERMELHO in m for m in mensagens)


def test_opcao_de_habilidade_mostra_mana_e_dano_previsto():
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  from rpg.dados.habilidades import HABILIDADES
  descricao = batalha._descricao_habilidade(personagem, HABILIDADES['Investida'], monstro)
  assert 'mana' in descricao
  assert 'dano' in descricao


def test_fuga_bem_sucedida_termina_em_fuga(monkeypatch):
  personagem = _personagem_cavaleiro()
  monkeypatch.setattr(batalha.random, 'randint', lambda a, b: 1)  # força sucesso na fuga

  resultado, _monstro = batalha.batalhar(
      personagem, MONSTROS['Slime'], escrever=lambda *_a, **_k: None,
      ler_acao=lambda titulo, opcoes, **kw: len(opcoes) - 1,  # sempre "Tentar fugir"
      aguardar=lambda: None)

  assert resultado == batalha.ResultadoBatalha.FUGA
