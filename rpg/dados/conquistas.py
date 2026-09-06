"""Diário de conquistas: cada conquista é só um predicado sobre o estado do
personagem (nada de sistema de eventos à parte) — mais simples e impossível
de dessincronizar, já que ela é sempre calculada na hora a partir do que já
existe (chefes derrotados, nível, missões etc.)."""

from dataclasses import dataclass
from typing import Callable

from .dungeons import DUNGEONS
from .especializacoes import ESPECIALIZACOES
from .itens import ACESSORIOS_UNICOS_POR_NOME, ARMADURAS_UNICAS, ARMAS_LENDARIAS
from .sidequests import SIDEQUESTS

# Ids dos baús/itens do mundo aberto (ver rpg/jogo.py `_eventos_ilyrath`/
# `_eventos_vethgard`) — usado só pra "achou tudo que existe até agora".
TOTAL_COLETAVEIS_MUNDO = 6


@dataclass(frozen=True)
class Conquista:
  id: str
  nome: str
  descricao: str
  verificar: Callable[[object], bool]
  recompensa_exp: int = 0
  recompensa_moedas: int = 0


def _tem_acessorio_unico_equipado(p):
  return any(nome in p.acessorios_equipados for nome in ACESSORIOS_UNICOS_POR_NOME)


def _todas_sidequests_completas(p):
  return all(sid in p.sidequests_completadas for sid in SIDEQUESTS)


def _todos_chefes_principais_derrotados(p):
  chefes = {andar.chefe for dungeon in DUNGEONS.values() for andar in dungeon.andares}
  return chefes.issubset(set(p.chefes_derrotados))


def _tem_todos_acessorios_unicos(p):
  posse = set(p.acessorios_guardados) | set(p.acessorios_equipados)
  return set(ACESSORIOS_UNICOS_POR_NOME) <= posse


def _tem_arma_lendaria(p):
  nomes_lendarias = {a.nome for a in ARMAS_LENDARIAS.values()}
  return (p.arma_equipada in nomes_lendarias
          or any(n in nomes_lendarias for n in p.equipamentos_guardados))


def _tem_armadura_unica(p):
  nomes_unicas = set(ARMADURAS_UNICAS)
  return (p.armadura_equipada in nomes_unicas
          or any(n in nomes_unicas for n in p.armaduras_guardadas))


def _tem_documento_de(cidade_doc):
  return lambda p: p.itens_especiais.get(cidade_doc, 0) > 0


def _tem_especializacao(nome):
  return lambda p: p.especializacao == nome


CONQUISTAS = {
  # ---------------------------------------------------------------- Combate
  'primeiro_sangue': Conquista(
      'primeiro_sangue', 'Primeiro Sangue', 'Derrote seu primeiro monstro.',
      lambda p: p.monstros_derrotados >= 1, recompensa_moedas=20),
  'cacador': Conquista(
      'cacador', 'Caçador', 'Derrote 50 monstros.',
      lambda p: p.monstros_derrotados >= 50, recompensa_moedas=100),
  'exterminador': Conquista(
      'exterminador', 'Exterminador', 'Derrote 200 monstros.',
      lambda p: p.monstros_derrotados >= 200, recompensa_moedas=300, recompensa_exp=500),
  'flagelo_dos_monstros': Conquista(
      'flagelo_dos_monstros', 'Flagelo dos Monstros', 'Derrote 500 monstros.',
      lambda p: p.monstros_derrotados >= 500, recompensa_moedas=800, recompensa_exp=1000),
  'lenda_da_cacada': Conquista(
      'lenda_da_cacada', 'Lenda da Caçada', 'Derrote 1000 monstros.',
      lambda p: p.monstros_derrotados >= 1000, recompensa_moedas=2000, recompensa_exp=2500),

  # -------------------------------------------------------------- Progressão
  'nivel_5': Conquista(
      'nivel_5', 'Primeiros Passos', 'Alcance o nível 5.',
      lambda p: p.nivel >= 5, recompensa_moedas=30),
  'nivel_10': Conquista(
      'nivel_10', 'Aprendiz Experiente', 'Alcance o nível 10.',
      lambda p: p.nivel >= 10, recompensa_moedas=50),
  'nivel_20': Conquista(
      'nivel_20', 'Combatente Forjado', 'Alcance o nível 20.',
      lambda p: p.nivel >= 20, recompensa_moedas=120),
  'nivel_30': Conquista(
      'nivel_30', 'Veterano', 'Alcance o nível 30.',
      lambda p: p.nivel >= 30, recompensa_moedas=200),
  'nivel_40': Conquista(
      'nivel_40', 'Guerreiro Consagrado', 'Alcance o nível 40.',
      lambda p: p.nivel >= 40, recompensa_moedas=350),
  'nivel_50': Conquista(
      'nivel_50', 'Lenda de Ilyrath', 'Alcance o nível 50.',
      lambda p: p.nivel >= 50, recompensa_moedas=500),
  'nivel_65': Conquista(
      'nivel_65', 'Ápice do Poder', 'Alcance o nível 65.',
      lambda p: p.nivel >= 65, recompensa_moedas=800),
  'nivel_75': Conquista(
      'nivel_75', 'Além dos Limites', 'Alcance o nível 75.',
      lambda p: p.nivel >= 75, recompensa_moedas=1200, recompensa_exp=1000),

  # ------------------------------------------------------------------ Chefes
  'primeiro_chefe': Conquista(
      'primeiro_chefe', 'Caçador de Chefes', 'Derrote seu primeiro chefe de dungeon.',
      lambda p: len(p.chefes_derrotados) >= 1, recompensa_moedas=80),
  'tres_chefes': Conquista(
      'tres_chefes', 'Trilha de Sangue', 'Derrote 3 chefes de dungeon diferentes.',
      lambda p: len(p.chefes_derrotados) >= 3, recompensa_moedas=250),
  'sete_chefes': Conquista(
      'sete_chefes', 'Colecionador de Coroas', 'Derrote 7 chefes de dungeon diferentes.',
      lambda p: len(p.chefes_derrotados) >= 7, recompensa_moedas=500, recompensa_exp=400),
  'todos_os_chefes': Conquista(
      'todos_os_chefes', 'Flagelo dos Chefes', 'Derrote todos os chefes principais de Ilyrath.',
      _todos_chefes_principais_derrotados, recompensa_moedas=800, recompensa_exp=800),
  'derrota_dragao_anciao': Conquista(
      'derrota_dragao_anciao', 'Caçador de Dragões', 'Derrote o Dragão Ancião de Habusken.',
      lambda p: 'Dragão Ancião de Habusken' in p.chefes_derrotados, recompensa_moedas=150),
  'derrota_arquiteto': Conquista(
      'derrota_arquiteto', 'Desmantelador', 'Derrote O Arquiteto, na Torre Arcana.',
      lambda p: 'O Arquiteto' in p.chefes_derrotados, recompensa_moedas=250),
  'derrota_kraken': Conquista(
      'derrota_kraken', 'Terror das Profundezas', 'Derrote o Kraken Ancestral.',
      lambda p: 'Kraken Ancestral' in p.chefes_derrotados, recompensa_moedas=400),
  'heroi_de_ilyrath': Conquista(
      'heroi_de_ilyrath', 'Herói de Ilyrath', 'Derrote Vashtar, o Rei Cinza.',
      lambda p: 'Vashtar, o Rei Cinza' in p.chefes_derrotados, recompensa_moedas=1000, recompensa_exp=1000),

  # -------------------------------------------------------------- Guilda
  'guilda_novato': Conquista(
      'guilda_novato', 'Membro da Guilda', 'Complete 5 missões da guilda.',
      lambda p: p.missoes_completadas >= 5, recompensa_moedas=60),
  'guilda_experiente': Conquista(
      'guilda_experiente', 'Rosto Conhecido', 'Complete 10 missões da guilda.',
      lambda p: p.missoes_completadas >= 10, recompensa_moedas=120),
  'guilda_veterano': Conquista(
      'guilda_veterano', 'Pilar da Guilda', 'Complete 20 missões da guilda.',
      lambda p: p.missoes_completadas >= 20, recompensa_moedas=250),
  'guilda_lendario': Conquista(
      'guilda_lendario', 'Nome na Guilda', 'Complete 50 missões da guilda.',
      lambda p: p.missoes_completadas >= 50, recompensa_moedas=600, recompensa_exp=400),
  'reputacao_experiente': Conquista(
      'reputacao_experiente', 'Reputação em Ascensão', 'Alcance o tier "Experiente" da guilda.',
      lambda p: p.reputacao_guilda >= 100, recompensa_moedas=80),
  'reputacao_veterano': Conquista(
      'reputacao_veterano', 'Confiança da Guilda', 'Alcance o tier "Veterano" da guilda.',
      lambda p: p.reputacao_guilda >= 300, recompensa_moedas=250),
  'reputacao_lendaria': Conquista(
      'reputacao_lendaria', 'Nome Lendário na Guilda', 'Alcance o tier "Lendário" da guilda.',
      lambda p: p.reputacao_guilda >= 600, recompensa_moedas=600, recompensa_exp=400),

  # ------------------------------------------------------- Mundo aberto
  'documentado': Conquista(
      'documentado', 'Cidadão de Ilyrath', 'Obtenha um documento de identidade de alguma cidade.',
      lambda p: bool(p.itens_especiais), recompensa_moedas=40),
  'passaporte_completo': Conquista(
      'passaporte_completo', 'Viajante Reconhecido', 'Obtenha os documentos de identidade de Habusken e Vethgard.',
      lambda p: _tem_documento_de('Selo de Habusken')(p) and _tem_documento_de('Selo de Vethgard')(p),
      recompensa_moedas=150),
  'bom_samaritano': Conquista(
      'bom_samaritano', 'Bom Samaritano', 'Complete todas as sidequests conhecidas.',
      _todas_sidequests_completas, recompensa_moedas=300, recompensa_exp=300),
  'explorador': Conquista(
      'explorador', 'Explorador', 'Encontre 3 baús ou itens escondidos pelo mundo aberto.',
      lambda p: len(p.mundo_coletados) >= 3, recompensa_moedas=60),
  'explorador_completo': Conquista(
      'explorador_completo', 'Não Deixou Pedra sobre Pedra',
      'Encontre todos os baús e itens conhecidos do mundo aberto.',
      lambda p: len(p.mundo_coletados) >= TOTAL_COLETAVEIS_MUNDO, recompensa_moedas=200, recompensa_exp=150),

  # ---------------------------------------------------------- Equipamento
  'colecionador': Conquista(
      'colecionador', 'Colecionador', 'Equipe um acessório único de chefe.',
      _tem_acessorio_unico_equipado, recompensa_moedas=100),
  'colecionador_completo': Conquista(
      'colecionador_completo', 'Cofre Andante', 'Obtenha todos os 13 acessórios únicos de chefe.',
      _tem_todos_acessorios_unicos, recompensa_moedas=1500, recompensa_exp=1000),
  'forjador_lendario': Conquista(
      'forjador_lendario', 'Forjador Lendário', 'Obtenha a arma lendária da sua classe.',
      _tem_arma_lendaria, recompensa_moedas=300),
  'armadura_das_profundezas': Conquista(
      'armadura_das_profundezas', 'Vestido para a Guerra', 'Obtenha uma armadura única de crafting.',
      _tem_armadura_unica, recompensa_moedas=300),
  'encantador': Conquista(
      'encantador', 'Toque Arcano', 'Encante um equipamento pela primeira vez.',
      lambda p: p.encantamento_arma > 0 or p.encantamento_armadura > 0, recompensa_moedas=40),
  'encantador_mestre': Conquista(
      'encantador_mestre', 'Mestre do Encantamento', 'Leve o encantamento da arma ao máximo.',
      lambda p: p.encantamento_arma >= 30, recompensa_moedas=400, recompensa_exp=300),
  'bolsos_maiores': Conquista(
      'bolsos_maiores', 'Bolsos Maiores', 'Compre todos os slots extras de acessório.',
      lambda p: p.slots_acessorio_comprados >= 3, recompensa_moedas=150),
  'arsenal_completo': Conquista(
      'arsenal_completo', 'Arsenal Completo', 'Compre todos os slots extras de habilidade.',
      lambda p: p.slots_habilidade_comprados >= 2, recompensa_moedas=150),

  # ------------------------------------------------------------ Riqueza
  'poupanca': Conquista(
      'poupanca', 'Começando a Poupar', 'Acumule 1.000 cobres ganhos ao longo do jogo.',
      lambda p: p.moedas_totais_ganhas >= 1000, recompensa_moedas=50),
  'comerciante': Conquista(
      'comerciante', 'Comerciante Nato', 'Acumule 10.000 cobres ganhos ao longo do jogo.',
      lambda p: p.moedas_totais_ganhas >= 10000, recompensa_moedas=200),
  'magnata': Conquista(
      'magnata', 'Magnata de Ilyrath', 'Acumule 100.000 cobres ganhos ao longo do jogo.',
      lambda p: p.moedas_totais_ganhas >= 100000, recompensa_moedas=1000, recompensa_exp=500),

  # ------------------------------------------------------- Especialização
  'especializado': Conquista(
      'especializado', 'Especialista', 'Escolha uma especialização.',
      lambda p: bool(p.especializacao), recompensa_moedas=100),
  'piromante': Conquista(
      'piromante', 'Mestre das Chamas', 'Torne-se um Piromante.',
      _tem_especializacao('Piromante'), recompensa_moedas=120),
  'criomante': Conquista(
      'criomante', 'Mestre do Gelo', 'Torne-se um Criomante.',
      _tem_especializacao('Criomante'), recompensa_moedas=120),
  'paladino': Conquista(
      'paladino', 'Guerreiro Sagrado', 'Torne-se um Paladino.',
      _tem_especializacao('Paladino'), recompensa_moedas=120),
  'berserker': Conquista(
      'berserker', 'Fúria Encarnada', 'Torne-se um Berserker.',
      _tem_especializacao('Berserker'), recompensa_moedas=120),
  'batedor': Conquista(
      'batedor', 'Sombra da Estrada', 'Torne-se um Batedor.',
      _tem_especializacao('Batedor'), recompensa_moedas=120),
  'atirador_de_elite': Conquista(
      'atirador_de_elite', 'Mira Impecável', 'Torne-se um Atirador de Elite.',
      _tem_especializacao('Atirador de Elite'), recompensa_moedas=120),
}

assert set(ESPECIALIZACOES) == {
  'Piromante', 'Criomante', 'Paladino', 'Berserker', 'Batedor', 'Atirador de Elite',
}, 'uma especialização nova foi adicionada sem a conquista correspondente'
