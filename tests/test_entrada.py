"""Testes de regressão para a leitura de tecla: Espaço tem que confirmar
igual Enter, sem afetar entrada de texto livre (que usa `input()`, não
`ler_tecla()` — ver Mestre de Habusken em test_cidade.py, que digita
letras separadas por espaço via `input()` normalmente)."""

import msvcrt

from rpg import entrada


def test_espaco_confirma_igual_enter(monkeypatch):
  teclas = iter([b' '])
  monkeypatch.setattr(msvcrt, 'getch', lambda: next(teclas))

  assert entrada._ler_tecla_windows() == entrada.ENTER


def test_enter_continua_confirmando(monkeypatch):
  teclas = iter([b'\r'])
  monkeypatch.setattr(msvcrt, 'getch', lambda: next(teclas))

  assert entrada._ler_tecla_windows() == entrada.ENTER


def test_menu_de_verdade_aceita_espaco_pra_escolher_opcao(monkeypatch):
  """Teste de ponta a ponta com o leitor de tecla real (só o `msvcrt.getch`
  mockado): desce uma opção com seta e confirma apertando Espaço."""
  teclas = iter([b'\xe0', b'P', b' '])  # seta pra baixo (2 bytes), depois espaço
  monkeypatch.setattr(msvcrt, 'getch', lambda: next(teclas))

  escolha = entrada.menu('Teste', ['A', 'B', 'C'], leitor=entrada._ler_tecla_windows,
                          escrever=lambda *_a, **_k: None, limpar=lambda: None)

  assert escolha == 1


def test_menu_com_secoes_mostra_cabecalho_sem_afetar_navegacao():
  """Cabeçalhos de seção são só desenho — não entram em `opcoes`, então não
  mudam índice nenhum nem viram opção selecionável."""
  linhas = []

  escolha = entrada.menu(
      'Teste', ['A', 'B', 'C'], secoes={0: 'GRUPO 1', 2: 'GRUPO 2'},
      leitor=lambda: entrada.ENTER, escrever=linhas.append, limpar=lambda: None)

  assert escolha == 0  # Enter na primeira chamada, índice inicial 0 — igual sem `secoes`
  texto = '\n'.join(linhas)
  assert 'GRUPO 1' in texto
  assert 'GRUPO 2' in texto
  # o cabeçalho do grupo 2 tem que aparecer DEPOIS da opção A e ANTES da C.
  assert texto.index('A') < texto.index('GRUPO 2') < texto.index('C')


def test_menu_sem_secoes_continua_funcionando_como_antes():
  escolha = entrada.menu('Teste', ['A', 'B'], leitor=lambda: entrada.ENTER,
                          escrever=lambda *_a, **_k: None, limpar=lambda: None)
  assert escolha == 0
