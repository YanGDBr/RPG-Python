"""Salvamento em JSON, em 3 save slots — sem conta/senha, só personagens.

O arquivo mora numa pasta padrão do sistema operacional (ver `config.py`),
não mais do lado do executável — assim o save sobrevive a reconstruções do
.exe e não depende de rodar sempre da mesma pasta.
"""

import dataclasses
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import ARQUIVO_SAVE, DIRETORIO_BACKUPS, NUMERO_DE_SLOTS
from .modelos.personagem import Personagem

PREFIXO_BACKUP = 'backup_saves_'

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


def exportar_backup() -> Path:
  """Copia o save atual (os 3 slots) pra um arquivo com carimbo de data/hora
  na pasta de backups — pra não perder o progresso ao atualizar/reinstalar o
  jogo, ou só por segurança antes de uma atualização. Devolve o caminho
  completo do arquivo criado; levanta `FileNotFoundError` se não existe save
  ainda."""
  if not ARQUIVO_SAVE.exists():
    raise FileNotFoundError('Nenhum save encontrado ainda.')
  DIRETORIO_BACKUPS.mkdir(parents=True, exist_ok=True)
  carimbo = datetime.now().strftime('%Y%m%d_%H%M%S')
  destino = DIRETORIO_BACKUPS / f'{PREFIXO_BACKUP}{carimbo}.json'
  shutil.copy(ARQUIVO_SAVE, destino)
  return destino


def listar_backups() -> List[Path]:
  """Backups na pasta de backups, do mais recente para o mais antigo."""
  if not DIRETORIO_BACKUPS.exists():
    return []
  return sorted(DIRETORIO_BACKUPS.glob(f'{PREFIXO_BACKUP}*.json'), reverse=True)


def importar_backup(origem: Path):
  """Substitui o save atual pelo conteúdo do arquivo de backup indicado.
  Valida que o arquivo é um JSON de verdade antes de sobrescrever o save
  real — levanta `ValueError`/`OSError` se o arquivo não existir ou não for
  um backup válido, sem tocar no save atual nesse caso."""
  if not origem.exists():
    raise FileNotFoundError(f'Arquivo não encontrado: {origem}')
  with open(origem, 'r', encoding='utf-8') as arquivo:
    conteudo = json.load(arquivo)  # valida o JSON antes de sobrescrever
  if not isinstance(conteudo, dict):
    raise ValueError('Esse arquivo não parece ser um backup de save válido.')
  ARQUIVO_SAVE.parent.mkdir(parents=True, exist_ok=True)
  shutil.copy(origem, ARQUIVO_SAVE)
