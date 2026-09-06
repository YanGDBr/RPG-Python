"""Diário de conquistas: cada conquista é só um predicado sobre o estado do
personagem (nada de sistema de eventos à parte) — mais simples e impossível
de dessincronizar, já que ela é sempre calculada na hora a partir do que já
existe (chefes derrotados, nível, missões etc.)."""

from dataclasses import dataclass
from typing import Callable

from .dungeons import DUNGEONS
from .itens import ACESSORIOS_UNICOS_POR_NOME
from .sidequests import SIDEQUESTS


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


CONQUISTAS = {
  'primeiro_sangue': Conquista(
      'primeiro_sangue', 'Primeiro Sangue', 'Derrote seu primeiro monstro.',
      lambda p: p.monstros_derrotados >= 1, recompensa_moedas=20),
  'cacador': Conquista(
      'cacador', 'Caçador', 'Derrote 50 monstros.',
      lambda p: p.monstros_derrotados >= 50, recompensa_moedas=100),
  'exterminador': Conquista(
      'exterminador', 'Exterminador', 'Derrote 200 monstros.',
      lambda p: p.monstros_derrotados >= 200, recompensa_moedas=300, recompensa_exp=500),
  'nivel_10': Conquista(
      'nivel_10', 'Aprendiz Experiente', 'Alcance o nível 10.',
      lambda p: p.nivel >= 10, recompensa_moedas=50),
  'nivel_30': Conquista(
      'nivel_30', 'Veterano', 'Alcance o nível 30.',
      lambda p: p.nivel >= 30, recompensa_moedas=200),
  'nivel_50': Conquista(
      'nivel_50', 'Lenda de Ilyrath', 'Alcance o nível 50.',
      lambda p: p.nivel >= 50, recompensa_moedas=500),
  'primeiro_chefe': Conquista(
      'primeiro_chefe', 'Caçador de Chefes', 'Derrote seu primeiro chefe de dungeon.',
      lambda p: len(p.chefes_derrotados) >= 1, recompensa_moedas=80),
  'todos_os_chefes': Conquista(
      'todos_os_chefes', 'Flagelo dos Chefes', 'Derrote todos os chefes principais de Ilyrath.',
      _todos_chefes_principais_derrotados, recompensa_moedas=800, recompensa_exp=800),
  'especializado': Conquista(
      'especializado', 'Especialista', 'Escolha uma especialização.',
      lambda p: bool(p.especializacao), recompensa_moedas=100),
  'colecionador': Conquista(
      'colecionador', 'Colecionador', 'Equipe um acessório único de chefe.',
      _tem_acessorio_unico_equipado, recompensa_moedas=100),
  'guilda_novato': Conquista(
      'guilda_novato', 'Membro da Guilda', 'Complete 5 missões da guilda.',
      lambda p: p.missoes_completadas >= 5, recompensa_moedas=60),
  'guilda_veterano': Conquista(
      'guilda_veterano', 'Pilar da Guilda', 'Complete 20 missões da guilda.',
      lambda p: p.missoes_completadas >= 20, recompensa_moedas=250),
  'documentado': Conquista(
      'documentado', 'Cidadão de Ilyrath', 'Obtenha um documento de identidade de alguma cidade.',
      lambda p: bool(p.itens_especiais), recompensa_moedas=40),
  'bom_samaritano': Conquista(
      'bom_samaritano', 'Bom Samaritano', 'Complete todas as sidequests conhecidas.',
      _todas_sidequests_completas, recompensa_moedas=300, recompensa_exp=300),
  'heroi_de_ilyrath': Conquista(
      'heroi_de_ilyrath', 'Herói de Ilyrath', 'Derrote Vashtar, o Rei Cinza.',
      lambda p: 'Vashtar, o Rei Cinza' in p.chefes_derrotados, recompensa_moedas=1000, recompensa_exp=1000),
}
