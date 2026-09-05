"""Helpers de renderização de tela: limpar terminal, barras de progresso, cabeçalhos."""

import os
import re

from .config import Cor

_CODIGO_ANSI = re.compile(r'\033\[[0-9;]*m')


def largura_visivel(texto):
  """Comprimento do texto sem contar os códigos de cor ANSI."""
  return len(_CODIGO_ANSI.sub('', texto))


def ljust_visivel(texto, largura, preenchimento=' '):
  """Como `str.ljust`, mas contando só os caracteres visíveis — texto com
  código de cor embutido faria o ljust normal contar bytes invisíveis e
  desalinhar qualquer caixa/coluna desenhada em ASCII."""
  faltam = largura - largura_visivel(texto)
  return texto + preenchimento * max(0, faltam)


def limpar_tela():
  os.system('cls' if os.name == 'nt' else 'clear')


def barra(atual, maximo, largura=20, cor=None):
  proporcao = 0.0 if maximo <= 0 else max(0.0, min(1.0, atual / maximo))
  preenchido = round(largura * proporcao)
  vazio = '-' * (largura - preenchido)
  if cor:
    parte_cheia = f'{cor}{"#" * preenchido}{Cor.RESET}'
  else:
    parte_cheia = '#' * preenchido
  return f'[{parte_cheia}{vazio}] {atual}/{maximo}'


def cabecalho(titulo):
  linha = '=' * (len(titulo) + 4)
  return f'{Cor.NEGRITO}{linha}\n  {titulo}\n{linha}{Cor.RESET}'
