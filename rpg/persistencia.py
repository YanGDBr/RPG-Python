"""Salvamento em JSON, em 3 save slots — sem conta/senha, só personagens.

O arquivo mora numa pasta padrão do sistema operacional (ver `config.py`),
não mais do lado do executável — assim o save sobrevive a reconstruções do
.exe e não depende de rodar sempre da mesma pasta.
"""

import dataclasses
import json
from typing import List, Optional

from .config import ARQUIVO_SAVE, NUMERO_DE_SLOTS
from .modelos.personagem import Personagem

_CAMPOS_VALIDOS = {campo.name for campo in dataclasses.fields(Personagem)}


def carregar_slots() -> List[Optional[Personagem]]:
  if not ARQUIVO_SAVE.exists():
    return [None] * NUMERO_DE_SLOTS

  with open(ARQUIVO_SAVE, 'r', encoding='utf-8') as arquivo:
    dados_brutos = json.load(arquivo)

  slots: List[Optional[Personagem]] = []
  for indice in range(NUMERO_DE_SLOTS):
    dados_slot = dados_brutos.get(str(indice))
    if dados_slot is None:
      slots.append(None)
    else:
      filtrados = {chave: valor for chave, valor in dados_slot.items()
                   if chave in _CAMPOS_VALIDOS}
      slots.append(Personagem(**filtrados))
  return slots


def salvar_slots(slots: List[Optional[Personagem]]):
  dados_brutos = {
    str(indice): dataclasses.asdict(personagem) if personagem else None
    for indice, personagem in enumerate(slots)
  }
  ARQUIVO_SAVE.parent.mkdir(parents=True, exist_ok=True)
  with open(ARQUIVO_SAVE, 'w', encoding='utf-8') as arquivo:
    json.dump(dados_brutos, arquivo, ensure_ascii=False, indent=2)
