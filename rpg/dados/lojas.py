"""Agrupamentos de catálogo usados pelas telas de loja."""

from .itens import ACESSORIOS, ARMADURAS, ARMAS, ITENS_CONSUMIVEIS, POCOES

COMIDAS_VENDIDAS = ['Bife', 'Frango', 'Arroz']

CATALOGO_ACESSORIOS = list(ACESSORIOS.values())
CATALOGO_ITENS_CONSUMIVEIS = list(ITENS_CONSUMIVEIS.values())
CATALOGO_POCOES = list(POCOES.values())
CATALOGO_ARMADURAS = list(ARMADURAS.values())


def armas_disponiveis_para_classe(classe: str):
  return [arma for arma in ARMAS.values() if arma.classe == classe]
