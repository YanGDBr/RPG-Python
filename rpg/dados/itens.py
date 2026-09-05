"""Catálogo de tudo que existe fora de monstros e habilidades: armas, armaduras,
acessórios, poções, itens consumíveis e materiais de crafting.
"""

from ..modelos.item import Acessorio, Armadura, Arma, ItemConsumivel, Material, Pocao

# --------------------------------------------------------------------- Armas
# 1 arma inicial (grátis, em classes.py) + 2 tiers compráveis por classe.
ARMAS = {
  'Cajado de Madeira Velha': Arma('Cajado de Madeira Velha', 20, preco=70, classe='Mago', nivel_minimo=5),
  'Cajado Rúnico': Arma('Cajado Rúnico', 35, elemento='Fogo', preco=300, classe='Mago', nivel_minimo=15),

  'Espada de Ferro': Arma('Espada de Ferro', 20, preco=70, classe='Cavaleiro', nivel_minimo=5),
  'Espada Flamejante': Arma('Espada Flamejante', 35, elemento='Fogo', preco=300, classe='Cavaleiro', nivel_minimo=15),

  'Arco de Madeira': Arma('Arco de Madeira', 25, preco=70, classe='Arqueiro', nivel_minimo=5),
  'Arco Élfico': Arma('Arco Élfico', 40, preco=300, classe='Arqueiro', nivel_minimo=15),
}

# Armas lendárias — só obtidas via crafting com material de chefe final de cada dungeon.
ARMAS_LENDARIAS = {
  'Mago': Arma('Cajado do Arquiteto', 70, elemento='Sombrio', classe='Mago', nivel_minimo=30),
  'Cavaleiro': Arma('Espada do Dragão Ancião', 70, elemento='Fogo', classe='Cavaleiro', nivel_minimo=30),
  'Arqueiro': Arma('Arco do Vazio', 70, elemento='Sombrio', classe='Arqueiro', nivel_minimo=30),
}

# ----------------------------------------------------------------- Armaduras
ARMADURAS = {
  'Armadura de Couro': Armadura('Armadura de Couro', '10% a mais de vida', bonus_vida_percentual=10, preco=100),
  'Armadura de Cobre': Armadura('Armadura de Cobre', '15% a mais de vida e 5% a mais de mana',
                                  bonus_vida_percentual=15, bonus_mana_percentual=5, preco=200),
  'Armadura de Prata': Armadura('Armadura de Prata', '25% a mais de vida e 10% a mais de mana',
                                  bonus_vida_percentual=25, bonus_mana_percentual=10, preco=400),
  'Armadura Dracônica': Armadura('Armadura Dracônica', '40% a mais de vida e 20% a mais de mana',
                                   bonus_vida_percentual=40, bonus_mana_percentual=20, preco=800),
}

# ---------------------------------------------------------------- Acessórios
ACESSORIOS = {
  'Colar do Labirinto': Acessorio(
      'Colar do Labirinto', 'Aumenta a chance de achar a sala do chefe', 'boss', 5, preco=90),
  'Pulseira Sagrada': Acessorio(
      'Pulseira Sagrada', 'Aumenta a vida e a mana máximas em 25', 'mana_vida', 25, preco=100),
  'Anel de Fogo': Acessorio(
      'Anel de Fogo', 'O inimigo começa a batalha em Queimadura por 3 turnos', 'queimadura_inicial', 3, preco=130),
  'Bracelete da Sorte': Acessorio(
      'Bracelete da Sorte', 'Aumenta a chance de crítico em 10%', 'critico', 10, preco=150),
}

# -------------------------------------------------------------------- Poções
POCOES = {
  'Vida': Pocao('Vida', 'vida', 60, preco=30),
  'Mana': Pocao('Mana', 'mana', 60, preco=30),
  'Esquiva': Pocao('Esquiva', 'esquiva', 15, preco=80),
  'Poder': Pocao('Poder', 'poder', 10, preco=50),
}

# Só obtida via crafting (ver receitas.py).
POCOES_CRAFTADAS = {
  'Fúria': Pocao('Fúria', 'critico', 20, preco=0),
}

# ------------------------------------------------------------- Itens comuns
ITENS_CONSUMIVEIS = {
  'Perfume Anti-Monstro': ItemConsumivel(
      'Perfume Anti-Monstro', 'anti_monstro', 4, 'Diminui a chance de ser atacado por um monstro', preco=50),
  'Perfume Monstro': ItemConsumivel(
      'Perfume Monstro', 'monstro', 2, 'Aumenta a chance de ser atacado por um monstro', preco=50),
  'Drop Buffer': ItemConsumivel(
      'Drop Buffer', 'drop', 20, 'Aumenta os drops e a chance de dropar itens', preco=150),
}

# --------------------------------------------------------------- Comidas
PRECO_COMIDA = 20

# ---------------------------------------------------------------- Materiais
MATERIAIS = {
  'Gosma de Slime': Material('Gosma de Slime', 'Material comum, dropado por slimes.'),
  'Presa de Lobo': Material('Presa de Lobo', 'Presa afiada de lobo.'),
  'Escama de Salamandra': Material('Escama de Salamandra', 'Escama resistente ao fogo.'),
  'Ectoplasma': Material('Ectoplasma', 'Resíduo de criaturas espectrais.'),
  'Cristal Arcano': Material('Cristal Arcano', 'Cristal imbuído de energia mágica.'),
  'Núcleo do Dragão Ancião': Material('Núcleo do Dragão Ancião', 'Coração cristalizado do Dragão Ancião de Habusken.'),
  'Fragmento do Arquiteto': Material('Fragmento do Arquiteto', 'Um fragmento do ser que construiu a Torre Arcana.'),
}
