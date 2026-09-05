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
