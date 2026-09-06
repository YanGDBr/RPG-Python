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


def test_diario_ganhou_muito_mais_conquistas():
  """Pedido explícito do usuário: aumentar muito o diário."""
  from rpg.dados.conquistas import CONQUISTAS
  assert len(CONQUISTAS) >= 45


def test_forjador_lendario_reconhece_arma_guardada_ou_equipada():
  from rpg.dados.conquistas import CONQUISTAS
  personagem = _personagem()
  assert not CONQUISTAS['forjador_lendario'].verificar(personagem)

  personagem.equipamentos_guardados = ['Espada do Dragão Ancião']
  assert CONQUISTAS['forjador_lendario'].verificar(personagem)


def test_colecionador_completo_exige_todos_os_13_acessorios_unicos():
  from rpg.dados.conquistas import CONQUISTAS
  from rpg.dados.itens import ACESSORIOS_UNICOS_POR_NOME
  personagem = _personagem()
  personagem.acessorios_guardados = list(ACESSORIOS_UNICOS_POR_NOME)[:-1]
  assert not CONQUISTAS['colecionador_completo'].verificar(personagem)

  personagem.acessorios_guardados = list(ACESSORIOS_UNICOS_POR_NOME)
  assert CONQUISTAS['colecionador_completo'].verificar(personagem)


def test_passaporte_completo_exige_os_dois_selos():
  from rpg.dados.conquistas import CONQUISTAS
  personagem = _personagem()
  personagem.adicionar_item_especial('Selo de Habusken')
  assert not CONQUISTAS['passaporte_completo'].verificar(personagem)

  personagem.adicionar_item_especial('Selo de Vethgard')
  assert CONQUISTAS['passaporte_completo'].verificar(personagem)


def test_conquista_de_cada_especializacao_verifica_a_especializacao_certa():
  from rpg.dados.conquistas import CONQUISTAS
  personagem = _personagem()
  personagem.especializacao = 'Berserker'

  assert CONQUISTAS['berserker'].verificar(personagem)
  assert not CONQUISTAS['piromante'].verificar(personagem)
