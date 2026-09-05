"""Helpers de renderização de tela: limpar terminal, barras de progresso, cabeçalhos."""

import os

from .config import Cor


def limpar_tela():
  os.system('cls' if os.name == 'nt' else 'clear')


def barra(atual, maximo, largura=20):
  proporcao = 0.0 if maximo <= 0 else max(0.0, min(1.0, atual / maximo))
  preenchido = round(largura * proporcao)
  return '[' + '#' * preenchido + '-' * (largura - preenchido) + f'] {atual}/{maximo}'


def cabecalho(titulo):
  linha = '=' * (len(titulo) + 4)
  return f'{Cor.NEGRITO}{linha}\n  {titulo}\n{linha}{Cor.RESET}'
