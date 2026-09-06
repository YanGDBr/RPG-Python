"""O personagem do jogador — um único dataclass plano, fácil de salvar em JSON.

Antes existiam duas classes (`conta`, que ficava no disco, e `Player`, uma cópia
carregada em memória) e uma função de 30 linhas copiando campo por campo entre
elas a cada salvamento. Aqui é um objeto só.
"""

import datetime
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Personagem:
  nome: str

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
  acoes_desde_desgaste_fome: int = 0

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
  # Começa com 1 slot; cada compra em `slots_acessorio_comprados` libera mais um
  # (até 3 comprados = 4 no total — ver CUSTOS_SLOT_ACESSORIO em config.py).
  acessorios_equipados: List[str] = field(default_factory=list)
  slots_acessorio_comprados: int = 0

  habilidades_aprendidas: List[str] = field(default_factory=list)
  habilidades_equipadas: List[str] = field(default_factory=list)
  cooldowns: Dict[str, int] = field(default_factory=dict)
  # Começa com 3 slots (as iniciais da classe); até 2 compráveis a mais (5 no
  # total) — ver CUSTOS_SLOT_HABILIDADE em config.py.
  slots_habilidade_comprados: int = 0

  efeitos_ativos: List[dict] = field(default_factory=list)
  itens_ativados: List[dict] = field(default_factory=list)

  chefes_derrotados: List[str] = field(default_factory=list)
  andar_atual: Dict[str, int] = field(
      default_factory=lambda: {'habusken': 1, 'torre_arcana': 1, 'abismo_submerso': 1,
                                 'cratera_vhalos': 1})
  torre_arcana_liberada: bool = False
  abismo_submerso_liberado: bool = False
  cratera_vhalos_liberado: bool = False
  abismo_epilogo_mostrado: bool = False

  # Cada missão: {dungeon_id, andar, quadro_indice, monstro, quantidade_alvo,
  # quantidade_atual, recompensa_exp, recompensa_moedas}. No máximo
  # MAX_MISSOES_ATIVAS (ver config.py) ao mesmo tempo.
  missoes_ativas: List[dict] = field(default_factory=list)
  maior_andar_visitado: Dict[str, int] = field(
      default_factory=lambda: {'habusken': 1, 'torre_arcana': 1, 'abismo_submerso': 1,
                                 'cratera_vhalos': 1})

  treinamento_habusken: int = 0
  eten: bool = False

  local: str = 'inicio'
  morto: bool = False

  # Bônus temporários que só duram a batalha atual (resetados em `iniciar_batalha`).
  bonus_dano_batalha: int = 0
  bonus_esquiva_batalha: int = 0
  bonus_critico_batalha: int = 0
  pocao_poder_usada: bool = False
  pocao_esquiva_usada: bool = False
  pocao_furia_usada: bool = False

  # Especialização (nível 30+) e o recurso de Fúria, exclusivo do Cavaleiro.
  especializacao: str = ''
  furia_cavaleiro: int = 0

  # Postura de combate: 'ofensiva' (mais dano, mais dano recebido) ou 'defensiva'.
  postura: str = 'ofensiva'

  # Foco do Arqueiro (recurso próprio) + elemento da flecha (troca de graça
  # em batalha, só vale pras habilidades de elemento Fisico "genérico").
  foco_arqueiro: int = 0
  elemento_flecha_atual: str = 'Fisico'

  # Ressonância Arcana do Mago: sobe ao conjurar um elemento diferente do
  # último, zera se repetir — recompensa variar em vez de martelar o mesmo.
  ressonancia_arcana: int = 0
  ultimo_elemento_conjurado: str = ''

  # Só 1 item por turno em batalha (não gasta turno, mas não empilha vários).
  item_usado_neste_turno: bool = False
  # Bônus de um único golpe canalizado (mini-jogo) — some sozinho depois de usado.
  bonus_canalizacao_pendente: int = 0

  # Reputação da guilda (sobe ao completar missão) e progresso pra encantamento.
  reputacao_guilda: int = 0
  encantamento_arma: int = 0
  encantamento_armadura: int = 0

  # Estatísticas cumulativas (tela de Estatísticas) e marcos de história.
  monstros_derrotados: int = 0
  moedas_totais_ganhas: int = 0
  missoes_completadas: int = 0
  historia_concluida: bool = False
  data_criacao: str = field(default_factory=lambda: datetime.date.today().isoformat())

  def vida_percentual(self) -> float:
    return 0.0 if self.vida_maxima <= 0 else self.vida / self.vida_maxima

  def mana_percentual(self) -> float:
    return 0.0 if self.mana_maxima <= 0 else self.mana / self.mana_maxima

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

  def remover_material(self, nome: str, quantidade: int = 1) -> bool:
    if self.materiais.get(nome, 0) < quantidade:
      return False
    self.materiais[nome] -= quantidade
    if self.materiais[nome] <= 0:
      del self.materiais[nome]
    return True
