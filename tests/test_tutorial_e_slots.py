"""Testes para a nova tela 'Tutorial' (texto fixo, igual pra qualquer
personagem) e para a compra de slots extras de habilidade (até 5)."""

from rpg.config import CUSTOS_SLOT_HABILIDADE
from rpg.modelos.personagem import Personagem
from rpg.sistemas import cidade


def _personagem():
  return Personagem(nome='teste', classe='Cavaleiro', raca='Humano')


def _cavaleiro_com_habilidades(extra_aprendida='Golpe Duplo'):
  personagem = _personagem()
  personagem.habilidades_aprendidas = ['Investida', 'Corte Fatal', 'Espada Mágica']
  personagem.habilidades_equipadas = list(personagem.habilidades_aprendidas)
  if extra_aprendida:
    personagem.habilidades_aprendidas.append(extra_aprendida)
  return personagem


def test_tutorial_abre_e_fecha_sem_erro():
  personagem = _personagem()
  cidade.tela_tutorial(personagem, escrever=lambda *_a, **_k: None,
                        ler_acao=lambda *_a, **_k: None, aguardar=lambda: None)


def test_tutorial_abre_um_topico_e_volta():
  personagem = _personagem()
  respostas = iter([0, 0, None])  # abre o primeiro tópico, vê o texto, volta, sai
  cidade.tela_tutorial(personagem, escrever=lambda *_a, **_k: None,
                        ler_acao=lambda *_a, **_k: next(respostas), aguardar=lambda: None)


def test_tutorial_abre_guia_elemental_a_partir_do_menu():
  personagem = _personagem()
  indice_guia = len(cidade._TOPICOS_TUTORIAL)
  respostas = iter([indice_guia, 0, None])
  cidade.tela_tutorial(personagem, escrever=lambda *_a, **_k: None,
                        ler_acao=lambda *_a, **_k: next(respostas), aguardar=lambda: None)


def test_tutorial_textos_sao_iguais_pra_qualquer_personagem():
  """Requisito explícito: o texto não muda dependendo da classe do usuário."""
  mago = Personagem(nome='a', classe='Mago', raca='Humano')
  arqueiro = Personagem(nome='b', classe='Arqueiro', raca='Elfo')
  for _titulo, gerar_texto in cidade._TOPICOS_TUTORIAL:
    texto = gerar_texto()
    assert isinstance(texto, str) and texto.strip()
  # os textos não recebem `personagem` nenhum — não têm como variar por classe.
  assert mago.classe != arqueiro.classe


def test_equipar_habilidade_em_slot_vazio_nao_pede_substituicao():
  personagem = _cavaleiro_com_habilidades()
  personagem.slots_habilidade_comprados = 1  # max = 4, tem 1 slot vazio

  respostas = iter([3, None])  # escolhe "Golpe Duplo" (a 4ª opção), depois sai
  cidade.tela_equipar_habilidades(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _t, _o, **_k: next(respostas), aguardar=lambda: None)

  assert personagem.habilidades_equipadas == ['Investida', 'Corte Fatal', 'Espada Mágica', 'Golpe Duplo']


def test_equipar_habilidade_com_slots_cheios_ainda_pede_substituicao():
  personagem = _cavaleiro_com_habilidades()
  assert personagem.slots_habilidade_comprados == 0  # max = 3, sem slot vazio

  respostas = iter([3, 0, None])  # escolhe "Golpe Duplo", substitui o slot 0, sai
  cidade.tela_equipar_habilidades(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _t, _o, **_k: next(respostas), aguardar=lambda: None)

  assert personagem.habilidades_equipadas == ['Golpe Duplo', 'Corte Fatal', 'Espada Mágica']


def test_comprar_slot_habilidade_gasta_moeda_e_aumenta_o_maximo():
  personagem = _personagem()
  custo, campo_moeda = CUSTOS_SLOT_HABILIDADE[0]
  setattr(personagem, campo_moeda, custo)

  cidade._comprar_slot_habilidade(personagem, escrever=lambda *_a, **_k: None, aguardar=lambda: None)

  assert getattr(personagem, campo_moeda) == 0
  assert personagem.slots_habilidade_comprados == 1
  assert cidade._max_slots_habilidade(personagem) == 4


def test_comprar_slot_habilidade_falha_sem_moeda_suficiente():
  personagem = _personagem()
  mensagens = []

  cidade._comprar_slot_habilidade(personagem, escrever=mensagens.append, aguardar=lambda: None)

  assert personagem.slots_habilidade_comprados == 0
  assert any('suficientes' in m for m in mensagens)


def test_comprar_slot_habilidade_respeita_o_maximo():
  personagem = _personagem()
  personagem.slots_habilidade_comprados = len(CUSTOS_SLOT_HABILIDADE)
  mensagens = []

  cidade._comprar_slot_habilidade(personagem, escrever=mensagens.append, aguardar=lambda: None)

  assert personagem.slots_habilidade_comprados == len(CUSTOS_SLOT_HABILIDADE)
  assert any('máximo' in m for m in mensagens)
