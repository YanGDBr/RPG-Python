"""Testes de regressão para o balanceamento das missões da guilda."""

from rpg.dados.monstros import MONSTROS
from rpg.modelos.personagem import Personagem
from rpg.sistemas import economia


def _personagem_baixo_nivel():
  p = Personagem(nome='teste', senha_hash='x', classe='Cavaleiro', raca='Humano')
  p.nivel = 1
  return p


def test_missoes_podem_incluir_monstros_de_andares_avancados_mesmo_com_nivel_baixo():
  """Regressão: o sorteio de missão só considerava monstros até nivel+10 do
  personagem, então quem já tinha avançado pelas dungeons (mas continuava
  com o nível de personagem baixo) nunca via missão dos monstros que estava
  enfrentando de verdade."""
  personagem = _personagem_baixo_nivel()
  candidatos_de_nivel_alto = [nome for nome, m in MONSTROS.items()
                              if not m.chefe and m.nivel > personagem.nivel + 10]
  assert candidatos_de_nivel_alto, 'preparação de teste inválida: nenhum monstro de nível alto encontrado'

  # gera muitas rodadas de missões e confirma que, eventualmente, um monstro
  # de nível bem mais alto do que o personagem aparece no sorteio.
  encontrou_nivel_alto = False
  for _ in range(200):
    missoes = economia.gerar_missoes(personagem)
    if any(m['monstro'] in candidatos_de_nivel_alto for m in missoes):
      encontrou_nivel_alto = True
      break
  assert encontrou_nivel_alto


def test_recompensa_da_missao_escala_com_nivel_do_monstro():
  personagem = _personagem_baixo_nivel()
  missoes = economia.gerar_missoes(personagem)
  for missao in missoes:
    monstro = MONSTROS[missao['monstro']]
    assert missao['recompensa_exp'] == missao['quantidade'] * monstro.nivel * 2
    assert missao['recompensa_moedas'] == missao['quantidade'] * monstro.nivel * 3
