"""Especializações desbloqueadas no nível 30 — cada classe se ramifica em 2
caminhos, cada um com uma passiva e uma habilidade exclusiva (concedida
automaticamente ao escolher, sem precisar comprar/desbloquear à parte)."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Especializacao:
  nome: str
  classe: str
  descricao: str
  habilidade_nova: str
  bonus_tipo: str    # 'dano_elemento' | 'vida_maxima' | 'dano_vida_baixa' | 'esquiva_flat' | 'critico'
  bonus_valor: int
  bonus_elemento: Optional[str] = None


ESPECIALIZACOES = {
  'Piromante': Especializacao(
      'Piromante', 'Mago', 'Mestre do fogo: +20% de dano em habilidades de Fogo.',
      'Explosão Solar', 'dano_elemento', 20, bonus_elemento='Fogo'),
  'Criomante': Especializacao(
      'Criomante', 'Mago', 'Mestre do gelo: +20% de dano em habilidades de Gelo.',
      'Fúria Glacial', 'dano_elemento', 20, bonus_elemento='Gelo'),
  'Paladino': Especializacao(
      'Paladino', 'Cavaleiro', 'Guerreiro sagrado: +15% de vida máxima.',
      'Julgamento', 'vida_maxima', 15),
  'Berserker': Especializacao(
      'Berserker', 'Cavaleiro', 'Fúria de batalha: +25% de dano quando sua vida está abaixo de 50%.',
      'Fúria Sanguinária', 'dano_vida_baixa', 25),
  'Batedor': Especializacao(
      'Batedor', 'Arqueiro', 'Especialista em evasão: +15 pontos de esquiva.',
      'Tiro Certeiro', 'esquiva_flat', 15),
  'Atirador de Elite': Especializacao(
      'Atirador de Elite', 'Arqueiro', 'Mira impecável: +20% de chance de crítico.',
      'Tiro Perfurante', 'critico', 20),
}

ESPECIALIZACOES_POR_CLASSE = {
  'Mago': ['Piromante', 'Criomante'],
  'Cavaleiro': ['Paladino', 'Berserker'],
  'Arqueiro': ['Batedor', 'Atirador de Elite'],
}

NIVEL_MINIMO_ESPECIALIZACAO = 30
