from dataclasses import dataclass
from typing import List

from ..modelos.item import Arma
from .habilidades import HABILIDADES_INICIAIS


@dataclass(frozen=True)
class Classe:
  nome: str
  habilidades_iniciais: List[str]
  arma_inicial: Arma
  descricao: str


CLASSES = {
  'Mago': Classe(
      nome='Mago',
      habilidades_iniciais=HABILIDADES_INICIAIS['Mago'],
      arma_inicial=Arma(nome='Cajado Básico', bonus_poder_percentual=0),
      descricao='Ataca à distância com magia elemental. Frágil, mas com dano alto.'),
  'Cavaleiro': Classe(
      nome='Cavaleiro',
      habilidades_iniciais=HABILIDADES_INICIAIS['Cavaleiro'],
      arma_inicial=Arma(nome='Espada Básica', bonus_poder_percentual=0),
      descricao='Combate corpo a corpo, resistente e com dano consistente.'),
  'Arqueiro': Classe(
      nome='Arqueiro',
      habilidades_iniciais=HABILIDADES_INICIAIS['Arqueiro'],
      arma_inicial=Arma(nome='Arco Básico', bonus_poder_percentual=0),
      descricao='Ataques múltiplos à distância, ótimo contra grupos de inimigos.'),
}
