"""Testes do motor de sidequests de NPC (oferecer/progredir/entregar) — ver
rpg/dados/sidequests.py pro catálogo e rpg/sistemas/sidequests.py pro motor."""

from rpg.modelos.personagem import Personagem
from rpg.sistemas import sidequests


def _personagem():
  return Personagem(nome='teste', classe='Cavaleiro', raca='Humano')


def test_oferece_sidequest_ainda_nao_aceita():
  personagem = _personagem()
  respostas = iter([None])  # não aceita nem recusa explicitamente (Esc/inválido)
  mensagens = []

  sidequests.interagir(personagem, 'ecos_da_cantiga', mensagens.append,
                        lambda *_a, **_k: next(respostas), lambda: None)

  assert personagem.sidequests_ativas == []


def test_aceitar_sidequest_adiciona_em_ativas():
  personagem = _personagem()
  mensagens = []

  sidequests.interagir(personagem, 'ecos_da_cantiga', mensagens.append,
                        lambda *_a, **_k: 0, lambda: None)  # 0 = 'Aceitar'

  assert personagem.sidequests_ativas == [{'id': 'ecos_da_cantiga', 'progresso': 0}]
  assert any('aceita' in m.lower() for m in mensagens)


def test_sidequest_de_derrotar_nao_entrega_antes_de_completar_progresso():
  personagem = _personagem()
  personagem.sidequests_ativas = [{'id': 'ecos_da_cantiga', 'progresso': 2}]
  mensagens = []
  chamadas_menu = []

  sidequests.interagir(personagem, 'ecos_da_cantiga', mensagens.append,
                        lambda *a, **k: chamadas_menu.append(a) or 0, lambda: None)

  assert personagem.sidequests_ativas == [{'id': 'ecos_da_cantiga', 'progresso': 2}]
  assert any('2/5' in m for m in mensagens)
  assert chamadas_menu == []  # não chega a perguntar nada, só mostra progresso


def test_sidequest_de_derrotar_completa_e_concede_recompensa():
  personagem = _personagem()
  personagem.sidequests_ativas = [{'id': 'ecos_da_cantiga', 'progresso': 5}]
  exp_antes, moedas_antes = personagem.exp, personagem.moeda_cobre

  sidequests.interagir(personagem, 'ecos_da_cantiga', lambda *_a, **_k: None,
                        lambda *_a, **_k: 0, lambda: None)  # 0 = 'Entregar'

  assert personagem.sidequests_ativas == []
  assert 'ecos_da_cantiga' in personagem.sidequests_completadas
  assert personagem.exp == exp_antes + 200
  assert personagem.moeda_cobre == moedas_antes + 80


def test_sidequest_de_entregar_item_precisa_do_item_especial():
  personagem = _personagem()
  personagem.sidequests_ativas = [{'id': 'lenco_da_familia', 'progresso': 0}]
  mensagens = []

  sidequests.interagir(personagem, 'lenco_da_familia', mensagens.append,
                        lambda *_a, **_k: 0, lambda: None)

  assert personagem.sidequests_ativas == [{'id': 'lenco_da_familia', 'progresso': 0}]
  assert any('precisa' in m.lower() for m in mensagens)


def test_sidequest_de_entregar_item_completa_e_consome_o_item():
  personagem = _personagem()
  personagem.sidequests_ativas = [{'id': 'lenco_da_familia', 'progresso': 0}]
  personagem.adicionar_item_especial('Lenço da Família de Mikel')

  sidequests.interagir(personagem, 'lenco_da_familia', lambda *_a, **_k: None,
                        lambda *_a, **_k: 0, lambda: None)

  assert 'lenco_da_familia' in personagem.sidequests_completadas
  assert personagem.itens_especiais.get('Lenço da Família de Mikel', 0) == 0


def test_sidequest_de_entregar_material_completa_e_consome_material():
  personagem = _personagem()
  personagem.sidequests_ativas = [{'id': 'cristal_para_sorel', 'progresso': 0}]
  personagem.adicionar_material('Cristal Arcano')

  sidequests.interagir(personagem, 'cristal_para_sorel', lambda *_a, **_k: None,
                        lambda *_a, **_k: 0, lambda: None)

  assert 'cristal_para_sorel' in personagem.sidequests_completadas
  assert personagem.materiais.get('Cristal Arcano', 0) == 0


def test_sidequest_ja_completada_nao_interage_de_novo():
  personagem = _personagem()
  personagem.sidequests_completadas = ['ecos_da_cantiga']
  chamadas_menu = []

  sidequests.interagir(personagem, 'ecos_da_cantiga', lambda *_a, **_k: None,
                        lambda *a, **k: chamadas_menu.append(a) or 0, lambda: None)

  assert chamadas_menu == []


def test_registrar_derrota_avanca_apenas_sidequest_com_alvo_certo():
  personagem = _personagem()
  personagem.sidequests_ativas = [{'id': 'ecos_da_cantiga', 'progresso': 0}]  # alvo: Lobo

  sidequests.registrar_derrota(personagem, 'Kobold', lambda *_a, **_k: None)
  assert personagem.sidequests_ativas[0]['progresso'] == 0

  sidequests.registrar_derrota(personagem, 'Lobo', lambda *_a, **_k: None)
  assert personagem.sidequests_ativas[0]['progresso'] == 1
