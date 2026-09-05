"""Estrutura de cada dungeon: andares, monstros comuns e chefe de cada um.

Isso é o que elimina de vez o bug antigo de "andar 2 buscando monstro do andar
1" — como a exploração (rpg/sistemas/exploracao.py) é uma função só que lê os
dados do andar atual, não existe mais um andar "esquecido" com cópia errada.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Andar:
  numero: int
  nome: str
  faixa_nivel: str
  monstros_comuns: List[str]
  chefe: str
  chance_encontrar_chefe: int = 8    # 1 em N tentativas de exploração


@dataclass(frozen=True)
class Dungeon:
  id: str
  nome: str
  andares: List[Andar]
  requer_chefe_derrotado: Optional[str] = None


DUNGEONS = {
  'habusken': Dungeon(
      id='habusken',
      nome='Dungeon de Habusken',
      andares=[
        Andar(1, 'Caverna dos Slimes', 'Recomendado para níveis 1 a 5',
              ['Slime', 'Slime', 'Slime', 'Kobold', 'Kobold', 'Lobo'], 'Slime Gigante'),
        Andar(2, 'Covil dos Goblins', 'Recomendado para níveis 5 a 10',
              ['Goblin', 'Goblin', 'Goblin', 'Esqueleto', 'Kobold Mago', 'Esqueleto'], 'Goblin Xamã'),
        Andar(3, 'Profundezas de Pedra', 'Recomendado para níveis 15 a 20',
              ['Golem de Pedra', 'Aranha Gigante', 'Orc Guerreiro'], 'Orc Chefe'),
        Andar(4, 'Cripta Amaldiçoada', 'Recomendado para níveis 20 a 25',
              ['Zumbi', 'Fantasma', 'Cavaleiro Amaldiçoado'], 'Cavaleiro da Morte'),
        Andar(5, 'Covil do Dragão', 'Recomendado para níveis 25 a 30',
              ['Wyvern Jovem', 'Salamandra de Fogo', 'Golem de Obsidiana'], 'Dragão Ancião de Habusken'),
      ]),
  'torre_arcana': Dungeon(
      id='torre_arcana',
      nome='Torre Arcana',
      requer_chefe_derrotado='Dragão Ancião de Habusken',
      andares=[
        Andar(1, 'Salão dos Aprendizes', 'Recomendado para níveis 30+',
              ['Aprendiz Rebelde', 'Constructo Arcano', 'Grimório Vivo'], 'Arquimago Renegado'),
        Andar(2, 'Câmara Elemental', 'Recomendado para níveis 35+',
              ['Elemental de Gelo', 'Elemental de Raio', 'Guardião Espectral'], 'Guardiã da Torre'),
        Andar(3, 'Núcleo da Torre', 'Recomendado para níveis 40+',
              ['Homúnculo', 'Golem Arcano', 'Espectro do Vazio'], 'O Arquiteto'),
      ]),
}
