"""Definição estática de uma habilidade de classe."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Habilidade:
  nome: str
  mana: int
  dano_base: int
  tipo: str                       # 'ataque' | 'ataque_multiplo' | 'buff'
  elemento: str = 'Fisico'
  efeito: Optional[str] = None
  turnos_efeito: int = 0
  acertos_min: int = 1
  acertos_max: int = 1
  cooldown_max: int = 0
  bonus_critico: int = 0          # pontos percentuais extra de chance de crítico
  descricao: str = ''
  nivel_minimo: int = 1
  preco: int = 0
