"""Testes de regressão para o bug relatado: telas mostravam um aviso e já
voltavam pro menu (que limpa a tela) sem dar tempo de ler nada."""

from rpg.modelos.personagem import Personagem
from rpg.sistemas import cidade


def _personagem():
  return Personagem(nome='teste', senha_hash='x', classe='Cavaleiro', raca='Humano')


def test_mestre_habusken_pausa_ao_rejeitar_jogador_sem_boss_derrotado():
  personagem = _personagem()  # ainda não derrotou o Slime Gigante
  chamadas_aguardar = []

  cidade.tela_mestre_habusken(
      personagem, escrever=lambda *_a, **_k: None,
      aguardar=lambda: chamadas_aguardar.append(1))

  assert len(chamadas_aguardar) >= 1


def test_curandeira_pausa_quando_nao_tem_moedas():
  personagem = _personagem()
  personagem.moeda_cobre = 0
  chamadas_aguardar = []

  respostas_menu = iter([0, None])  # escolhe "Restaurar vida", depois sai

  def _fake_menu(_titulo, _opcoes, **_kw):
    return next(respostas_menu)

  cidade.tela_curandeira(
      personagem, escrever=lambda *_a, **_k: None, ler_acao=_fake_menu,
      entrada_texto=lambda *_a, **_k: '50',
      aguardar=lambda: chamadas_aguardar.append(1))

  assert len(chamadas_aguardar) >= 1


def test_status_pausa_sem_pontos_disponiveis():
  personagem = _personagem()
  personagem.pontos_status = 0
  chamadas_aguardar = []

  respostas_menu = iter([0, None])  # tenta +5 Vida máxima, depois sai

  def _fake_menu(_titulo, _opcoes, **_kw):
    return next(respostas_menu)

  cidade.tela_status(
      personagem, escrever=lambda *_a, **_k: None, ler_acao=_fake_menu,
      aguardar=lambda: chamadas_aguardar.append(1))

  assert len(chamadas_aguardar) >= 1
