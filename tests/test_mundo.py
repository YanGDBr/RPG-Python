"""Testes do motor de exploração do mundo aberto (diálogo/viagem, nunca
batalha) — mesmo padrão de dependências injetáveis usado em exploracao.py."""

from rpg.modelos.personagem import Personagem
from rpg.sistemas import mundo


def _personagem():
  return Personagem(nome='teste', classe='Cavaleiro', raca='Humano')


def _leitor(sequencia):
  fila = list(sequencia)
  return lambda: fila.pop(0)


def test_explorar_mapa_anda_ate_evento_e_retorna_resultado():
  mapa = ('#####', '#E.N#', '#####')
  eventos = {'N': lambda p, e, a, l: 'chegou'}

  resultado = mundo.explorar_mapa(
      _personagem(), mapa, eventos, 'Teste',
      escrever=lambda *_a, **_k: None,
      leitor_tecla=_leitor(['direita', 'direita']),
      limpar=lambda: None, aguardar=lambda: None)

  assert resultado == 'chegou'


def test_explorar_mapa_esc_retorna_none_sem_disparar_evento():
  mapa = ('#####', '#E.N#', '#####')
  chamadas = []
  eventos = {'N': lambda p, e, a, l: chamadas.append(1) or 'chegou'}

  resultado = mundo.explorar_mapa(
      _personagem(), mapa, eventos, 'Teste',
      escrever=lambda *_a, **_k: None,
      leitor_tecla=_leitor(['esc']),
      limpar=lambda: None, aguardar=lambda: None)

  assert resultado is None
  assert chamadas == []


def test_evento_que_retorna_none_nao_encerra_exploracao():
  """Um evento de diálogo (retorna None) só mostra a fala e deixa o jogador
  continuar andando — só um evento que retorna algo diferente de None
  encerra a exploração desse mapa."""
  mapa = ('######', '#E.N.#', '######')
  eventos = {'N': lambda p, e, a, l: None}

  resultado = mundo.explorar_mapa(
      _personagem(), mapa, eventos, 'Teste',
      escrever=lambda *_a, **_k: None,
      leitor_tecla=_leitor(['direita', 'direita', 'esc']),
      limpar=lambda: None, aguardar=lambda: None)

  assert resultado is None


def test_falar_com_npc_mostra_as_falas_e_aguarda(monkeypatch):
  from rpg.dados.npcs import Npc, NPCS
  monkeypatch.setitem(NPCS, 'npc_teste', Npc('Fulano', lambda p: ['Olá.', 'Tudo bem?']))
  mensagens = []
  chamadas_aguardar = []

  callback = mundo.falar_com_npc('npc_teste')
  resultado = callback(_personagem(), mensagens.append, lambda: chamadas_aguardar.append(1), lambda: None)

  assert resultado is None
  assert any('Fulano' in m for m in mensagens)
  assert any('Olá.' in m for m in mensagens)
  assert len(chamadas_aguardar) == 1
