"""Testes do diário de conquistas: cada conquista é um predicado sobre o
personagem, concedido (com recompensa) só na primeira vez que é visto como
cumprido — ver rpg/dados/conquistas.py e cidade.tela_diario_conquistas."""

from rpg.modelos.personagem import Personagem
from rpg.sistemas import cidade


def _personagem():
  return Personagem(nome='teste', classe='Cavaleiro', raca='Humano')


def test_sem_progresso_nenhuma_conquista_desbloqueada():
  personagem = _personagem()
  novas = cidade._verificar_novas_conquistas(personagem, lambda *_a, **_k: None)
  assert novas == []
  assert personagem.conquistas_desbloqueadas == []


def test_derrotar_primeiro_monstro_desbloqueia_conquista_e_concede_recompensa():
  personagem = _personagem()
  personagem.monstros_derrotados = 1
  moedas_antes = personagem.moeda_cobre

  novas = cidade._verificar_novas_conquistas(personagem, lambda *_a, **_k: None)

  assert [c.id for c in novas] == ['primeiro_sangue']
  assert 'primeiro_sangue' in personagem.conquistas_desbloqueadas
  assert personagem.moeda_cobre > moedas_antes


def test_conquista_ja_desbloqueada_nao_e_concedida_de_novo():
  personagem = _personagem()
  personagem.monstros_derrotados = 1
  cidade._verificar_novas_conquistas(personagem, lambda *_a, **_k: None)
  moedas_apos_primeira = personagem.moeda_cobre

  novas = cidade._verificar_novas_conquistas(personagem, lambda *_a, **_k: None)

  assert novas == []
  assert personagem.moeda_cobre == moedas_apos_primeira


def test_tela_diario_lista_conquistas_desbloqueadas_e_bloqueadas():
  from rpg.dados.conquistas import CONQUISTAS
  personagem = _personagem()
  personagem.monstros_derrotados = 1
  textos = []

  cidade.tela_diario_conquistas(personagem, escrever=lambda *_a, **_k: None,
                                 ler_acao=lambda titulo, *_a, **_k: textos.append(titulo),
                                 aguardar=lambda: None)

  texto = textos[0]
  assert CONQUISTAS['primeiro_sangue'].nome in texto
  assert f'(1/{len(CONQUISTAS)})' in texto


def test_todos_os_chefes_e_bom_samaritano_exigem_conjunto_completo():
  from rpg.dados.conquistas import CONQUISTAS
  from rpg.dados.dungeons import DUNGEONS
  from rpg.dados.sidequests import SIDEQUESTS
  personagem = _personagem()
  todos_chefes = [andar.chefe for dungeon in DUNGEONS.values() for andar in dungeon.andares]
  personagem.chefes_derrotados = todos_chefes[:-1]
  personagem.sidequests_completadas = list(SIDEQUESTS)[:-1]

  assert not CONQUISTAS['todos_os_chefes'].verificar(personagem)
  assert not CONQUISTAS['bom_samaritano'].verificar(personagem)

  personagem.chefes_derrotados = todos_chefes
  personagem.sidequests_completadas = list(SIDEQUESTS)

  assert CONQUISTAS['todos_os_chefes'].verificar(personagem)
  assert CONQUISTAS['bom_samaritano'].verificar(personagem)
