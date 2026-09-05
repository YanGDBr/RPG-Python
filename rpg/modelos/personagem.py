"""O personagem do jogador — um único dataclass plano, fácil de salvar em JSON.

Antes existiam duas classes (`conta`, que ficava no disco, e `Player`, uma cópia
carregada em memória) e uma função de 30 linhas copiando campo por campo entre
elas a cada salvamento. Aqui é um objeto só.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Personagem:
  nome: str
  senha_hash: str

  raca: str = ''
  classe: str = ''

  nivel: int = 1
  exp: int = 0
  exp_para_subir: int = 50
  pontos_status: int = 0

  vida: int = 100
  vida_maxima: int = 100
  mana: int = 100
  mana_maxima: int = 100
  poder: int = 0
  esquiva: int = 5
  sorte: int = 0

  moeda_cobre: int = 200
  moeda_prata: int = 0
  moeda_ouro: int = 0

  fome: int = 10
  descansos_usados: int = 0

  inventario: Dict[str, int] = field(default_factory=dict)
  materiais: Dict[str, int] = field(default_factory=dict)
  pocoes: Dict[str, int] = field(default_factory=dict)
  comidas: Dict[str, int] = field(
      default_factory=lambda: {'Bife': 4, 'Frango': 3, 'Arroz': 3})

  equipamentos_guardados: List[str] = field(default_factory=list)
  acessorios_guardados: List[str] = field(default_factory=list)
  armaduras_guardadas: List[str] = field(default_factory=list)

  arma_equipada: str = ''
  armadura_equipada: str = ''
  acessorio_equipado: str = ''

  habilidades_aprendidas: List[str] = field(default_factory=list)
  habilidades_equipadas: List[str] = field(default_factory=list)
  cooldowns: Dict[str, int] = field(default_factory=dict)

  efeitos_ativos: List[dict] = field(default_factory=list)
  itens_ativados: List[dict] = field(default_factory=list)

  chefes_derrotados: List[str] = field(default_factory=list)
  andar_atual: Dict[str, int] = field(
      default_factory=lambda: {'habusken': 1, 'torre_arcana': 1})
  torre_arcana_liberada: bool = False

  missao_monstro: str = ''
  missao_quantidade_alvo: int = 0
  missao_quantidade_atual: int = 0
  missao_recompensa_exp: int = 0
  missao_recompensa_moedas: int = 0

  treinamento_habusken: int = 0
  eten: bool = False

  local: str = 'inicio'
  morto: bool = False
  momento_reviver: Optional[str] = None

  # Bônus temporários que só duram a batalha atual (resetados em `iniciar_batalha`).
  bonus_dano_batalha: int = 0
  bonus_esquiva_batalha: int = 0
  bonus_critico_batalha: int = 0
  pocao_poder_usada: bool = False
  pocao_esquiva_usada: bool = False
  pocao_furia_usada: bool = False

  def vida_percentual(self) -> float:
    return 0.0 if self.vida_maxima <= 0 else self.vida / self.vida_maxima

  def mana_percentual(self) -> float:
    return 0.0 if self.mana_maxima <= 0 else self.mana / self.mana_maxima

  def curar_totalmente(self):
    self.vida = self.vida_maxima
    self.mana = self.mana_maxima
    self.efeitos_ativos.clear()

  def adicionar_item(self, nome: str, quantidade: int = 1):
    self.inventario[nome] = self.inventario.get(nome, 0) + quantidade

  def remover_item(self, nome: str, quantidade: int = 1) -> bool:
    if self.inventario.get(nome, 0) < quantidade:
      return False
    self.inventario[nome] -= quantidade
    if self.inventario[nome] <= 0:
      del self.inventario[nome]
    return True

  def adicionar_material(self, nome: str, quantidade: int = 1):
    self.materiais[nome] = self.materiais.get(nome, 0) + quantidade
