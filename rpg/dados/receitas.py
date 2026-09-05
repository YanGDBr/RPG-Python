"""Receitas de crafting: materiais dropados por monstros viram poções e, no
fim de jogo, a arma lendária de cada classe e a armadura abissal (usando
material dos chefes finais de cada dungeon)."""

from ..modelos.item import Receita

RECEITAS = {
  'Poção de Fúria': Receita(
      nome='Poção de Fúria',
      materiais_necessarios={'Escama de Salamandra': 2, 'Presa de Lobo': 1},
      resultado_tipo='pocao_craftada', resultado_nome='Fúria'),
  'Cajado do Arquiteto': Receita(
      nome='Cajado do Arquiteto',
      materiais_necessarios={'Núcleo do Dragão Ancião': 1, 'Fragmento do Arquiteto': 1},
      resultado_tipo='arma_lendaria', resultado_nome='Mago'),
  'Espada do Dragão Ancião': Receita(
      nome='Espada do Dragão Ancião',
      materiais_necessarios={'Núcleo do Dragão Ancião': 1, 'Fragmento do Arquiteto': 1},
      resultado_tipo='arma_lendaria', resultado_nome='Cavaleiro'),
  'Arco do Vazio': Receita(
      nome='Arco do Vazio',
      materiais_necessarios={'Núcleo do Dragão Ancião': 1, 'Fragmento do Arquiteto': 1},
      resultado_tipo='arma_lendaria', resultado_nome='Arqueiro'),
  'Armadura Abissal': Receita(
      nome='Armadura Abissal',
      materiais_necessarios={'Escama Abissal': 3, 'Pérola Negra': 2, 'Tinta de Kraken': 1},
      resultado_tipo='armadura_unica', resultado_nome='Armadura Abissal'),
}
