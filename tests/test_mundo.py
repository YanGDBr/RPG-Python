"""Testes do motor de exploração do mundo aberto: diálogo/viagem/coleta (sem
batalha) e zonas selvagens (com batalha) — mesmo padrão de dependências
injetáveis usado em exploracao.py."""

import re

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


def test_andar_no_mundo_desgasta_fome_por_passo():
  """Diferente da dungeon (só desgasta ao pisar num `?`), no mundo aberto
  cada passo de verdade conta — é o que o usuário pediu explicitamente. Usa
  um limiar bem maior que o da dungeon (ACOES_POR_DESGASTE_FOME_MUNDO), pra
  não zerar a fome depois de só alguns passos andando por aí."""
  from rpg.config import ACOES_POR_DESGASTE_FOME_MUNDO
  personagem = _personagem()
  fome_antes = personagem.fome
  corredor = '.' * (ACOES_POR_DESGASTE_FOME_MUNDO + 2)
  mapa = ('#' * (len(corredor) + 2), '#E' + corredor + '#', '#' * (len(corredor) + 2))

  mundo.explorar_mapa(
      personagem, mapa, {}, 'Teste',
      escrever=lambda *_a, **_k: None,
      leitor_tecla=_leitor(['direita'] * ACOES_POR_DESGASTE_FOME_MUNDO + ['esc']),
      limpar=lambda: None, aguardar=lambda: None)

  assert personagem.fome < fome_antes


def test_andar_no_mundo_gasta_fome_bem_mais_devagar_que_na_dungeon():
  """Regressão direta do pedido do usuário: no mesmo número de passos que
  zeraria a fome numa dungeon, o mundo aberto mal deveria arranhar a fome."""
  from rpg.config import ACOES_POR_DESGASTE_FOME
  personagem = _personagem()
  fome_antes = personagem.fome
  corredor = '.' * (ACOES_POR_DESGASTE_FOME + 2)
  mapa = ('#' * (len(corredor) + 2), '#E' + corredor + '#', '#' * (len(corredor) + 2))

  mundo.explorar_mapa(
      personagem, mapa, {}, 'Teste',
      escrever=lambda *_a, **_k: None,
      leitor_tecla=_leitor(['direita'] * ACOES_POR_DESGASTE_FOME + ['esc']),
      limpar=lambda: None, aguardar=lambda: None)

  assert personagem.fome == fome_antes  # nenhum desgaste ainda nesse número de passos


def test_mapa_do_mundo_exibe_a_fome_atual():
  personagem = _personagem()
  personagem.fome = 7
  mapa = ('#####', '#E..#', '#####')

  texto = mundo._desenhar_mapa(mapa, [1, 1], 'Teste', {}, personagem, {}, (5, 3))

  assert 'Fome 7/10' in texto


def test_janela_da_camera_mostra_so_uma_parte_de_mapa_grande():
  """Mapa bem maior que a janela — só uma fatia ao redor do jogador deve
  aparecer, não o mapa inteiro (é a "câmera" que revela aos poucos)."""
  largura, altura = 40, 20
  mapa = tuple(
      ('#' * largura) if y in (0, altura - 1) else ('#' + '.' * (largura - 2) + '#')
      for y in range(altura))
  mapa = list(mapa)
  mapa[altura // 2] = mapa[altura // 2][:1] + 'E' + mapa[altura // 2][2:]
  mapa = tuple(mapa)

  texto = mundo._desenhar_mapa(mapa, [altura // 2, 1], 'Teste', {}, _personagem(), {}, (15, 9))

  sem_cores = re.sub(r'\x1b\[[0-9;]*m', '', texto)
  linhas_da_grade = [linha for linha in sem_cores.split('\n')
                     if linha and all(len(token) == 1 for token in linha.split(' '))]
  assert len(linhas_da_grade) == 9
  assert all(len(linha.split(' ')) == 15 for linha in linhas_da_grade)


def test_zona_selvagem_pode_abrir_batalha(monkeypatch):
  from rpg.sistemas import mundo as modulo_mundo
  personagem = _personagem()
  mapa = ('#####', '#EF.#', '#####')

  monkeypatch.setattr(modulo_mundo.random, 'randint', lambda a, b: 1)  # sempre dispara o encontro
  chamadas_batalha = []

  def batalhar_fake(p, base, escrever=None, ler_acao=None, aguardar=None, limpar=None, **_kw):
    chamadas_batalha.append(base)
    from rpg.sistemas.batalha import ResultadoBatalha
    from rpg.modelos.monstro import MonstroBatalha
    monstro = MonstroBatalha.instanciar(base)
    monstro.vida = 0
    return ResultadoBatalha.VITORIA, monstro

  monkeypatch.setattr(modulo_mundo, 'batalhar', batalhar_fake)

  modulo_mundo.explorar_mapa(
      personagem, mapa, {}, 'Teste',
      escrever=lambda *_a, **_k: None,
      leitor_tecla=_leitor(['direita', 'esc']),
      limpar=lambda: None, aguardar=lambda: None,
      zonas_selvagens={'F': ['Slime']},
      ler_confirmacao=lambda *_a, **_k: True)

  assert len(chamadas_batalha) == 1
  assert chamadas_batalha[0].nome == 'Slime'


def test_zona_selvagem_recusar_nao_abre_batalha(monkeypatch):
  from rpg.sistemas import mundo as modulo_mundo
  personagem = _personagem()
  mapa = ('#####', '#EF.#', '#####')

  monkeypatch.setattr(modulo_mundo.random, 'randint', lambda a, b: 1)
  chamadas_batalha = []
  monkeypatch.setattr(modulo_mundo, 'batalhar', lambda *a, **k: chamadas_batalha.append(1))

  modulo_mundo.explorar_mapa(
      personagem, mapa, {}, 'Teste',
      escrever=lambda *_a, **_k: None,
      leitor_tecla=_leitor(['direita', 'esc']),
      limpar=lambda: None, aguardar=lambda: None,
      zonas_selvagens={'F': ['Slime']},
      ler_confirmacao=lambda *_a, **_k: False)

  assert chamadas_batalha == []


def test_abrir_bau_concede_recompensa_uma_unica_vez():
  personagem = _personagem()
  callback = mundo.abrir_bau('bau_teste_1', 'moedas', '', 50)

  callback(personagem, lambda *_a, **_k: None, lambda: None, lambda: None)
  saldo_apos_primeira = personagem.moeda_cobre

  callback(personagem, lambda *_a, **_k: None, lambda: None, lambda: None)

  assert saldo_apos_primeira == 250  # 200 iniciais + 50 do baú
  assert personagem.moeda_cobre == 250  # a segunda vez não concede de novo
  assert 'bau_teste_1' in personagem.mundo_coletados


def test_pegar_item_do_chao_concede_material_uma_vez():
  personagem = _personagem()
  callback = mundo.pegar_item_do_chao('item_teste_1', 'material', 'Gosma de Slime', 2)

  callback(personagem, lambda *_a, **_k: None, lambda: None, lambda: None)
  callback(personagem, lambda *_a, **_k: None, lambda: None, lambda: None)

  assert personagem.materiais.get('Gosma de Slime') == 2


def test_falar_com_npc_e_sidequest_mostra_fala_e_oferece_a_sidequest(monkeypatch):
  from rpg.dados.npcs import Npc, NPCS
  monkeypatch.setitem(NPCS, 'npc_teste', Npc('Fulano', lambda p: ['Olá.']))
  personagem = _personagem()
  mensagens = []

  callback = mundo.falar_com_npc_e_sidequest('npc_teste', 'ecos_da_cantiga',
                                              ler_acao=lambda *_a, **_k: 0)
  resultado = callback(personagem, mensagens.append, lambda: None, lambda: None)

  assert resultado is None
  assert any('Fulano' in m for m in mensagens)
  assert personagem.sidequests_ativas == [{'id': 'ecos_da_cantiga', 'progresso': 0}]
