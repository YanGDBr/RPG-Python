"""Invariantes gerais sobre o catálogo de monstros — coisas que valem pra
todo monstro/chefe do jogo, não um andar ou dungeon específico."""

from rpg.dados.monstros import MONSTROS

FINAIS_COM_FASE_FURIOSA = [
  'Dragão Ancião de Habusken',
  'O Arquiteto',
  'Kraken Ancestral',
  'Vashtar, o Rei Cinza',
]


def test_chefes_finais_de_cada_dungeon_tem_fase_furiosa():
  for nome in FINAIS_COM_FASE_FURIOSA:
    assert MONSTROS[nome].tem_fase_furiosa is True, f'{nome} deveria ter fase de fúria'


def test_todo_monstro_tem_pelo_menos_uma_descricao_de_ataque():
  for monstro in MONSTROS.values():
    assert len(monstro.descricoes_ataque) >= 1


def test_todo_monstro_tem_vida_e_ataque_positivos():
  for monstro in MONSTROS.values():
    assert monstro.vida_maxima > 0
    assert monstro.ataque_min > 0
    assert monstro.ataque_max >= monstro.ataque_min
