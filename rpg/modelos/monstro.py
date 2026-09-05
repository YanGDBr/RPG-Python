"""Molde de monstro (dado estático) e a instância viva usada durante uma batalha."""

from dataclasses import dataclass, field
from typing import List, Optional

from ..config import MULTIPLICADOR_ELITE_VIDA


@dataclass(frozen=True)
class MonstroBase:
  """Definição estática de um monstro — vive em rpg/dados/monstros.py."""

  nome: str
  vida_maxima: int
  ataque_min: int
  ataque_max: int
  nivel: int
  elemento: str = 'Fisico'
  fraquezas: tuple = ()
  resistencias: tuple = ()
  exp_min: int = 0
  exp_max: int = 0
  moedas_min: int = 0
  moedas_max: int = 0
  drops_item: tuple = ()          # ((nome_item, chance_0_a_1), ...)
  descricoes_ataque: tuple = ('ataca você',)
  efeito_aplicado: Optional[str] = None
  turnos_efeito_aplicado: int = 0
  chefe: bool = False

  # IA leve: alguns monstros fogem com pouca vida, outros telegrafam um golpe
  # forte um turno antes de desferi-lo.
  foge_com_pouca_vida: bool = False
  tem_investida_especial: bool = False


@dataclass
class MonstroBatalha:
  """Cópia mutável de um MonstroBase, com vida atual e efeitos ativos."""

  base: MonstroBase
  vida: int
  efeitos_ativos: List[dict] = field(default_factory=list)
  elite: bool = False
  carregando_investida: bool = False
  tentou_fugir: bool = False

  @classmethod
  def instanciar(cls, base: MonstroBase, elite: bool = False) -> 'MonstroBatalha':
    vida = round(base.vida_maxima * MULTIPLICADOR_ELITE_VIDA) if elite else base.vida_maxima
    return cls(base=base, vida=vida, elite=elite)

  @property
  def nome(self) -> str:
    return f'{"Elite " if self.elite else ""}{self.base.nome}'

  @property
  def vivo(self) -> bool:
    return self.vida > 0

  def receber_dano(self, dano: int):
    self.vida = max(0, self.vida - dano)
