"""Leitura de teclado multiplataforma e o widget de menu por setas/WASD.

Não depende do pacote `getkey` (abandonado, e quebrado no Windows porque
`msvcrt.getch()` retorna bytes e a lib tenta concatenar isso com uma str).
Aqui a leitura crua de tecla é feita direto com `msvcrt` (Windows) ou
`termios`/`tty` (Unix), normalizada para um pequeno conjunto de tokens.
"""

import os
import sys

CIMA = 'cima'
BAIXO = 'baixo'
ESQUERDA = 'esquerda'
DIREITA = 'direita'
ENTER = 'enter'
ESC = 'esc'


def _ler_tecla_windows():
  import msvcrt

  primeiro = msvcrt.getch()
  if primeiro in (b'\x00', b'\xe0'):
    segundo = msvcrt.getch()
    mapa = {b'H': CIMA, b'P': BAIXO, b'K': ESQUERDA, b'M': DIREITA}
    return mapa.get(segundo, '')
  if primeiro in (b'\r', b'\n'):
    return ENTER
  if primeiro == b'\x1b':
    return ESC
  if primeiro == b'\x03':
    raise KeyboardInterrupt
  try:
    return primeiro.decode('utf-8').lower()
  except UnicodeDecodeError:
    return ''


def _ler_tecla_unix():
  import select
  import termios
  import tty

  fd = sys.stdin.fileno()
  configuracao_antiga = termios.tcgetattr(fd)
  try:
    tty.setraw(fd)
    primeiro = sys.stdin.read(1)
    if primeiro == '\x1b':
      if select.select([sys.stdin], [], [], 0.05)[0]:
        resto = sys.stdin.read(2)
        mapa = {'[A': CIMA, '[B': BAIXO, '[C': DIREITA, '[D': ESQUERDA}
        return mapa.get(resto, ESC)
      return ESC
    if primeiro in ('\r', '\n'):
      return ENTER
    if primeiro == '\x03':
      raise KeyboardInterrupt
    return primeiro.lower()
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, configuracao_antiga)


def ler_tecla():
  """Lê uma única tecla do terminal e devolve um token normalizado."""
  if os.name == 'nt':
    return _ler_tecla_windows()
  return _ler_tecla_unix()


def menu(titulo, opcoes, *, indice_inicial=0, com_voltar=True,
         leitor=None, escrever=None, limpar=None):
  """Menu navegável por setas/WASD. Devolve o índice escolhido, ou None
  se o jogador cancelou (Esc) — só possível quando `com_voltar=True`.

  `leitor`, `escrever` e `limpar` são injetáveis para permitir testar o
  menu inteiro sem um terminal interativo de verdade.
  """
  from .interface import limpar_tela

  leitor = leitor or ler_tecla
  escrever = escrever or print
  limpar = limpar or limpar_tela

  destaque = '\033[7;1m'
  reset = '\033[0m'

  indice = indice_inicial % len(opcoes)
  while True:
    limpar()
    if titulo:
      escrever(titulo)
    for i, rotulo in enumerate(opcoes):
      if i == indice:
        # Reaplica o destaque depois de cada reset de cor embutido no rótulo,
        # senão a primeira cor dentro da opção quebraria o realce ao selecionar.
        rotulo_destacado = rotulo.replace(reset, reset + destaque)
        escrever(f'  {destaque}> {rotulo_destacado} {reset}')
      else:
        escrever(f'    {rotulo}')
    if com_voltar:
      escrever('\n(Esc para voltar)')

    tecla = leitor()
    if tecla in (CIMA, 'w'):
      indice = (indice - 1) % len(opcoes)
    elif tecla in (BAIXO, 's'):
      indice = (indice + 1) % len(opcoes)
    elif tecla == ENTER:
      return indice
    elif tecla == ESC and com_voltar:
      return None


def perguntar_sim_nao(pergunta, *, leitor=None, escrever=None, limpar=None):
  escolha = menu(pergunta, ['Sim', 'Não'], com_voltar=False,
                 leitor=leitor, escrever=escrever, limpar=limpar)
  return escolha == 0


def aguardar_leitura(mensagem=None, entrada=input):
  """Pausa até o jogador apertar Enter, antes de qualquer coisa que vá limpar
  a tela (a próxima chamada de `menu()`, por exemplo) — sem isso, o aviso que
  acabou de ser impresso desaparece antes de dar tempo de ler."""
  from .config import Cor
  entrada(mensagem or f'\n{Cor.VERDE}Pressione Enter para continuar...{Cor.RESET}')


def pedir_numero(pergunta, minimo=None, maximo=None, entrada=input, saida=print):
  """Pede um inteiro, repetindo até receber um valor válido dentro do intervalo."""
  while True:
    bruto = entrada(pergunta).strip()
    if not bruto.isdigit():
      saida('Digite apenas números.')
      continue
    valor = int(bruto)
    if minimo is not None and valor < minimo:
      saida(f'O valor mínimo é {minimo}.')
      continue
    if maximo is not None and valor > maximo:
      saida(f'O valor máximo é {maximo}.')
      continue
    return valor


def pedir_texto(pergunta, obrigatorio=True, entrada=input, saida=print):
  while True:
    valor = entrada(pergunta).strip()
    if valor or not obrigatorio:
      return valor
    saida('Esse campo não pode ficar vazio.')
