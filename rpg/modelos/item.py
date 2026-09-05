"""Dataclasses imutáveis para tudo que pode existir num inventário ou loja."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True)
class Arma:
  nome: str
  bonus_poder_percentual: int
  elemento: str = 'Fisico'
  preco: int = 0
  classe: Optional[str] = None
  nivel_minimo: int = 1


@dataclass(frozen=True)
class Armadura:
  nome: str
  descricao: str
  bonus_vida_percentual: int = 0
  bonus_mana_percentual: int = 0
  preco: int = 0


@dataclass(frozen=True)
class Acessorio:
  nome: str
  descricao: str
  efeito: str      # 'boss', 'mana_vida', 'queimadura_inicial', 'critico'
  valor: int
  preco: int = 0


@dataclass(frozen=True)
class Pocao:
  nome: str
  efeito: str      # 'vida', 'mana', 'esquiva', 'poder'
  valor: int
  preco: int = 0


@dataclass(frozen=True)
class ItemConsumivel:
  nome: str
  tipo: str        # 'anti_monstro', 'monstro', 'drop_buffer'
  valor: int
  descricao: str
  preco: int = 0


@dataclass(frozen=True)
class Material:
  nome: str
  descricao: str = ''


@dataclass(frozen=True)
class Receita:
  nome: str
  materiais_necessarios: Dict[str, int]
  resultado_tipo: str    # 'pocao' | 'item' | 'equipamento'
  resultado_nome: str
  quantidade_resultado: int = 1
