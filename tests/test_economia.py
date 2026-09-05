"""Testes de regressão para o balanceamento das missões da guilda."""

from rpg.dados.dungeons import DUNGEONS
from rpg.dados.monstros import MONSTROS
from rpg.modelos.personagem import Personagem
from rpg.sistemas import economia


def _personagem_baixo_nivel():
  p = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  p.nivel = 1
  return p


def test_quadro_do_andar_so_sorteia_monstros_daquele_andar():
  """O quadro de um andar tem que bater exatamente com o que o jogador
  enfrenta ali — nunca um monstro de outro andar/dungeon."""
  personagem = _personagem_baixo_nivel()
  andar = DUNGEONS['torre_arcana'].andares[2]  # Núcleo da Torre, nível 40+

  for _ in range(50):
    missoes = economia.gerar_missoes_do_andar(personagem, 'torre_arcana', 3)
    for missao in missoes:
      assert missao['monstro'] in andar.monstros_comuns
      assert missao['dungeon_id'] == 'torre_arcana'
      assert missao['andar'] == 3


def test_recompensa_da_missao_escala_com_nivel_do_monstro():
  personagem = _personagem_baixo_nivel()
  missoes = economia.gerar_missoes_do_andar(personagem, 'habusken', 1)
  for missao in missoes:
    monstro = MONSTROS[missao['monstro']]
    assert missao['recompensa_exp'] == missao['quantidade_alvo'] * monstro.nivel * 2
    assert missao['recompensa_moedas'] == missao['quantidade_alvo'] * monstro.nivel * 3


def test_aceitar_missao_respeita_limite_maximo():
  personagem = _personagem_baixo_nivel()
  missoes = economia.gerar_missoes_do_andar(personagem, 'habusken', 1)

  assert economia.aceitar_missao(personagem, missoes[0]) is True
  assert economia.aceitar_missao(personagem, missoes[1]) is True
  assert economia.aceitar_missao(personagem, missoes[2]) is False
  assert len(personagem.missoes_ativas) == 2


def test_missao_equipada_detecta_pela_origem_no_quadro():
  personagem = _personagem_baixo_nivel()
  missoes = economia.gerar_missoes_do_andar(personagem, 'habusken', 1)
  economia.aceitar_missao(personagem, missoes[0])

  assert economia.missao_equipada(personagem, missoes[0]) is True
  assert economia.missao_equipada(personagem, missoes[1]) is False


def test_abandonar_missao_remove_pelo_indice():
  personagem = _personagem_baixo_nivel()
  missoes = economia.gerar_missoes_do_andar(personagem, 'habusken', 1)
  economia.aceitar_missao(personagem, missoes[0])

  economia.abandonar_missao(personagem, 0)

  assert personagem.missoes_ativas == []
