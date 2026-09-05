from dataclasses import dataclass


@dataclass(frozen=True)
class Raca:
  nome: str
  bonus_tipo: str    # 'esquiva' | 'poder' | 'exp'
  valor: int
  descricao: str


RACAS = {
  'Fada': Raca('Fada', 'esquiva', 6, 'Aumenta a esquiva em 6 pontos.'),
  'Humano': Raca('Humano', 'poder', 10, 'Aumenta o dano causado em 10%.'),
  'Elfo': Raca('Elfo', 'exp', 25, 'Aumenta a experiência ganha em 25%.'),
}
