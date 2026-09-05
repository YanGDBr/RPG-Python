"""Receitas de crafting: materiais dropados por monstros viram poções e, no
fim de jogo, a arma lendária de cada classe (usando material dos dois chefes
finais)."""

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
}
