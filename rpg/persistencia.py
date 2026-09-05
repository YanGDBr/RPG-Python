"""Salvamento em JSON (no lugar do pickle) e hash de senha.

Antes o save era um dicionário de objetos `conta` serializado com pickle — além
de pickle poder executar código arbitrário ao carregar um arquivo malicioso,
o formato binário é impossível de inspecionar ou editar à mão. JSON resolve os
dois problemas e, como `Personagem` é um dataclass plano, salvar/carregar vira
uma linha (`dataclasses.asdict` / `Personagem(**dados)`).
"""

import dataclasses
import hashlib
import json
from typing import Dict

from .config import ARQUIVO_SAVE
from .modelos.personagem import Personagem

_CAMPOS_VALIDOS = {campo.name for campo in dataclasses.fields(Personagem)}


def gerar_hash_senha(senha: str) -> str:
  return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
  return gerar_hash_senha(senha) == hash_armazenado


def carregar_contas() -> Dict[str, Personagem]:
  if not ARQUIVO_SAVE.exists():
    return {}
  with open(ARQUIVO_SAVE, 'r', encoding='utf-8') as arquivo:
    dados_brutos = json.load(arquivo)

  contas = {}
  for nome, dados in dados_brutos.items():
    filtrados = {chave: valor for chave, valor in dados.items()
                 if chave in _CAMPOS_VALIDOS}
    contas[nome] = Personagem(**filtrados)
  return contas


def salvar_contas(contas: Dict[str, Personagem]):
  dados_brutos = {nome: dataclasses.asdict(personagem)
                   for nome, personagem in contas.items()}
  ARQUIVO_SAVE.parent.mkdir(parents=True, exist_ok=True)
  with open(ARQUIVO_SAVE, 'w', encoding='utf-8') as arquivo:
    json.dump(dados_brutos, arquivo, ensure_ascii=False, indent=2)


def salvar_personagem(contas: Dict[str, Personagem], personagem: Personagem):
  contas[personagem.nome] = personagem
  salvar_contas(contas)
