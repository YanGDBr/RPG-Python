"""Definição estática de uma habilidade de classe."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Habilidade:
  nome: str
  mana: int
  dano_base: int
  tipo: str                       # 'ataque' | 'ataque_multiplo' | 'ataque_area' | 'buff'
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

  # Mecânicas especiais das habilidades de especialização (nível 30+).
  custo_furia: int = 0             # se > 0, gasta Fúria do Cavaleiro em vez de mana
  custo_foco: int = 0              # se > 0, gasta Foco do Arqueiro em vez de mana
  sempre_critico: bool = False     # ignora a rolagem de crítico, sempre acerta crítico
  ignora_resistencia: bool = False  # trata resistência elemental do alvo como neutra
  cura_percentual_usuario: int = 0  # cura quem usou, em % da vida máxima
  efeito_no_usuario: Optional[str] = None  # aplica um efeito em quem usou (ex: Regeneração)
  turnos_efeito_no_usuario: int = 0

  # Habilidade interativa: pode ser "canalizada" (mini-jogo de memória) antes
  # de usar, fortalecendo o golpe conforme o acerto no mini-jogo.
  canalizavel: bool = False
