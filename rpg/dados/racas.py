from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Raca:
  nome: str
  bonus_tipo: str    # 'esquiva' | 'poder' | 'exp' | 'vida'
  valor: int
  descricao: str
  contrapartida_tipo: Optional[str] = None    # 'mana' (única contrapartida usada hoje)
  contrapartida_valor: int = 0


RACAS = {
  'Fada': Raca('Fada', 'esquiva', 6, 'Aumenta a esquiva em 6 pontos.'),
  'Humano': Raca('Humano', 'poder', 10, 'Aumenta o dano causado em 10%.'),
  'Elfo': Raca('Elfo', 'exp', 25, 'Aumenta a experiência ganha em 25%.'),
  'Anão': Raca('Anão', 'vida', 20, 'Aumenta a vida máxima em 20%, mas reduz a mana máxima em 15%.',
               contrapartida_tipo='mana', contrapartida_valor=15),
  'Orc': Raca('Orc', 'poder', 15, 'Aumenta o dano causado em 15%, mas reduz a mana máxima em 25% '
              '(guerreiro bruto, fraco em magia).', contrapartida_tipo='mana', contrapartida_valor=25),
}
