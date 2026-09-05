"""Resolve nome-do-item-equipado -> objeto de dado, e calcula os bônus efetivos.

No jogo original, os efeitos de acessório (Pulseira Sagrada aumentar vida/mana,
Anel de Fogo aplicar queimadura) praticamente nunca eram checados em lugar
nenhum — só o acessório de "achar sala do chefe" funcionava de verdade. Aqui
tudo passa por estas funções, então nenhum bônus fica esquecido.
"""

from ..dados.classes import CLASSES
from ..dados.itens import ACESSORIOS, ARMADURAS, ARMAS, ARMAS_LENDARIAS


def resolver_arma(personagem):
  arma_inicial = CLASSES[personagem.classe].arma_inicial
  nome = personagem.arma_equipada or arma_inicial.nome
  if nome == arma_inicial.nome:
    return arma_inicial
  if nome in ARMAS:
    return ARMAS[nome]
  for arma in ARMAS_LENDARIAS.values():
    if arma.nome == nome:
      return arma
  return arma_inicial


def resolver_armadura(personagem):
  return ARMADURAS.get(personagem.armadura_equipada)


def resolver_acessorio(personagem):
  return ACESSORIOS.get(personagem.acessorio_equipado)


def vida_maxima_efetiva(personagem):
  base = personagem.vida_maxima
  armadura = resolver_armadura(personagem)
  bonus_percentual = armadura.bonus_vida_percentual if armadura else 0
  acessorio = resolver_acessorio(personagem)
  bonus_fixo = acessorio.valor if acessorio and acessorio.efeito == 'mana_vida' else 0
  return round(base + base * bonus_percentual / 100) + bonus_fixo


def mana_maxima_efetiva(personagem):
  base = personagem.mana_maxima
  armadura = resolver_armadura(personagem)
  bonus_percentual = armadura.bonus_mana_percentual if armadura else 0
  acessorio = resolver_acessorio(personagem)
  bonus_fixo = acessorio.valor if acessorio and acessorio.efeito == 'mana_vida' else 0
  return round(base + base * bonus_percentual / 100) + bonus_fixo


def chance_critico_extra_acessorio(personagem):
  acessorio = resolver_acessorio(personagem)
  return acessorio.valor if acessorio and acessorio.efeito == 'critico' else 0


def chance_boss_extra_acessorio(personagem):
  acessorio = resolver_acessorio(personagem)
  return acessorio.valor if acessorio and acessorio.efeito == 'boss' else 0


def efeito_inicial_de_batalha_acessorio(personagem):
  """Anel de Fogo: aplica Queimadura no monstro assim que a batalha começa."""
  acessorio = resolver_acessorio(personagem)
  if acessorio and acessorio.efeito == 'queimadura_inicial':
    return ('Queimadura', acessorio.valor)
  return None
