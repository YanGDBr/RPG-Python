"""Testes de conteúdo/balanceamento da Cratera de Vhalos e do Rei Cinza:
Vashtar precisa ser o chefe mais difícil do jogo (pedido explícito do
usuário), e as recompensas pós-Vashtar (habilidades, armadura) têm que
existir e funcionar."""

from rpg.dados.dungeons import DUNGEONS
from rpg.dados.habilidades import HABILIDADES, HABILIDADES_DESBLOQUEAVEIS
from rpg.dados.itens import ARMADURAS_UNICAS
from rpg.dados.monstros import MONSTROS
from rpg.dados.receitas import RECEITAS
from rpg.modelos.personagem import Personagem
from rpg.sistemas import crafting

VASHTAR = 'Vashtar, o Rei Cinza'


def test_vashtar_e_o_chefe_com_mais_vida_do_jogo():
  chefes = [m for m in MONSTROS.values() if m.chefe]
  mais_vida = max(chefes, key=lambda m: m.vida_maxima)
  assert mais_vida.nome == VASHTAR


def test_vashtar_esta_entre_os_chefes_de_maior_ataque():
  chefes = [m for m in MONSTROS.values() if m.chefe]
  mais_ataque = max(chefes, key=lambda m: m.ataque_max)
  assert mais_ataque.nome == VASHTAR


def test_vashtar_e_o_chefe_de_maior_nivel_do_jogo():
  """Regressão: o nível dos monstros da Cratera de Vhalos (dungeon final, só
  libera depois de derrotar o Kraken Ancestral, nível 75) estava por engano
  mais baixo que o de dungeons anteriores — o chefe final tinha nível 50,
  menor até que chefes do meio do jogo."""
  chefes = [m for m in MONSTROS.values() if m.chefe]
  maior_nivel = max(chefes, key=lambda m: m.nivel)
  assert maior_nivel.nome == VASHTAR


def test_cratera_de_vhalos_tem_nivel_acima_da_dungeon_anterior():
  """O menor nível de monstro da Cratera de Vhalos precisa ficar acima do
  maior nível do Abismo Submerso (a dungeon que precisa ser zerada antes de
  liberar a Cratera) — senão a dungeon "final" fica mais fraca que a
  penúltima, o que não faz sentido de progressão."""
  nivel_maximo_abismo = max(
      MONSTROS[nome].nivel
      for andar in DUNGEONS['abismo_submerso'].andares
      for nome in [*andar.monstros_comuns, andar.chefe])
  nivel_minimo_cratera = min(
      MONSTROS[nome].nivel
      for andar in DUNGEONS['cratera_vhalos'].andares
      for nome in [*andar.monstros_comuns, andar.chefe])
  assert nivel_minimo_cratera > nivel_maximo_abismo


def test_vashtar_tem_investida_especial_e_nao_foge():
  vashtar = MONSTROS[VASHTAR]
  assert vashtar.tem_investida_especial is True
  assert vashtar.foge_com_pouca_vida is False


def test_cratera_de_vhalos_tem_dois_andares_terminando_em_vashtar():
  dungeon = DUNGEONS['cratera_vhalos']
  assert len(dungeon.andares) == 2
  assert dungeon.andares[-1].chefe == VASHTAR


def test_habilidades_pos_vashtar_exigem_nivel_50():
  nomes = ['Fogo Cinzento', 'Lâmina do Rei Caído', 'Flecha do Juízo']
  for nome in nomes:
    assert HABILIDADES[nome].nivel_minimo == 50
  for classe, lista in HABILIDADES_DESBLOQUEAVEIS.items():
    assert any(nome in lista for nome in nomes), f'{classe} sem habilidade pós-Vashtar'


def test_manto_do_rei_cinza_e_mais_forte_que_armadura_abissal():
  abissal = ARMADURAS_UNICAS['Armadura Abissal']
  manto = ARMADURAS_UNICAS['Manto do Rei Cinza']
  assert manto.bonus_vida_percentual > abissal.bonus_vida_percentual
  assert manto.bonus_mana_percentual > abissal.bonus_mana_percentual


def test_craftar_manto_do_rei_cinza_com_materiais_suficientes():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.adicionar_material('Cinza do Rei Corrompido', 3)

  sucesso = crafting.craftar(personagem, RECEITAS['Manto do Rei Cinza'], lambda *_a, **_k: None)

  assert sucesso is True
  assert 'Manto do Rei Cinza' in personagem.armaduras_guardadas
  assert personagem.materiais.get('Cinza do Rei Corrompido', 0) == 0
