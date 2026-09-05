import pytest

from rpg import persistencia
from rpg.modelos.personagem import Personagem


def _preparar_caminhos(tmp_path, monkeypatch):
  monkeypatch.setattr(persistencia, 'ARQUIVO_SAVE', tmp_path / 'saves.json')
  monkeypatch.setattr(persistencia, 'DIRETORIO_BACKUPS', tmp_path / 'backups')


def test_carregar_sem_arquivo_devolve_slots_vazios(tmp_path, monkeypatch):
  monkeypatch.setattr(persistencia, 'ARQUIVO_SAVE', tmp_path / 'nao_existe.json')
  slots = persistencia.carregar_slots()
  assert slots == [None, None, None]


def test_round_trip_salvar_e_carregar_slots(tmp_path, monkeypatch):
  caminho_falso = tmp_path / 'saves.json'
  monkeypatch.setattr(persistencia, 'ARQUIVO_SAVE', caminho_falso)

  personagem = Personagem(nome='Ana')
  personagem.nivel = 5
  personagem.inventario['Perfume Anti-Monstro'] = 2
  personagem.habilidades_equipadas = ['Investida', 'Corte Fatal', 'Espada Mágica']

  slots = [None, personagem, None]
  persistencia.salvar_slots(slots)
  assert caminho_falso.exists()

  carregados = persistencia.carregar_slots()
  assert carregados[0] is None
  assert carregados[2] is None
  assert carregados[1].nome == 'Ana'
  assert carregados[1].nivel == 5
  assert carregados[1].inventario['Perfume Anti-Monstro'] == 2
  assert carregados[1].habilidades_equipadas == ['Investida', 'Corte Fatal', 'Espada Mágica']


def test_apagar_slot_e_salvar_mantem_null(tmp_path, monkeypatch):
  caminho_falso = tmp_path / 'saves.json'
  monkeypatch.setattr(persistencia, 'ARQUIVO_SAVE', caminho_falso)

  slots = [Personagem(nome='Bob'), None, None]
  persistencia.salvar_slots(slots)

  slots_recarregados = persistencia.carregar_slots()
  slots_recarregados[0] = None  # apaga o personagem do slot 0
  persistencia.salvar_slots(slots_recarregados)

  slots_finais = persistencia.carregar_slots()
  assert slots_finais == [None, None, None]


def test_exportar_backup_sem_save_levanta_erro(tmp_path, monkeypatch):
  _preparar_caminhos(tmp_path, monkeypatch)

  with pytest.raises(FileNotFoundError):
    persistencia.exportar_backup()


def test_exportar_backup_cria_arquivo_na_pasta_de_backups(tmp_path, monkeypatch):
  _preparar_caminhos(tmp_path, monkeypatch)
  persistencia.salvar_slots([Personagem(nome='Ana'), None, None])

  destino = persistencia.exportar_backup()

  assert destino.exists()
  assert destino.parent == persistencia.DIRETORIO_BACKUPS
  assert destino.name.startswith(persistencia.PREFIXO_BACKUP)


def test_listar_backups_do_mais_recente_para_o_mais_antigo(tmp_path, monkeypatch):
  _preparar_caminhos(tmp_path, monkeypatch)
  persistencia.DIRETORIO_BACKUPS.mkdir(parents=True)
  antigo = persistencia.DIRETORIO_BACKUPS / f'{persistencia.PREFIXO_BACKUP}20200101_000000.json'
  novo = persistencia.DIRETORIO_BACKUPS / f'{persistencia.PREFIXO_BACKUP}20260101_000000.json'
  antigo.write_text('{}', encoding='utf-8')
  novo.write_text('{}', encoding='utf-8')

  backups = persistencia.listar_backups()

  assert backups == [novo, antigo]


def test_listar_backups_sem_pasta_devolve_lista_vazia(tmp_path, monkeypatch):
  _preparar_caminhos(tmp_path, monkeypatch)
  assert persistencia.listar_backups() == []


def test_importar_backup_restaura_conteudo_salvo(tmp_path, monkeypatch):
  _preparar_caminhos(tmp_path, monkeypatch)
  personagem = Personagem(nome='Ana')
  personagem.nivel = 9
  persistencia.salvar_slots([personagem, None, None])
  backup = persistencia.exportar_backup()

  # o save "atual" muda depois do backup...
  personagem.nivel = 1
  persistencia.salvar_slots([personagem, None, None])
  assert persistencia.carregar_slots()[0].nivel == 1

  # ...e importar o backup restaura o estado de quando ele foi tirado.
  persistencia.importar_backup(backup)
  assert persistencia.carregar_slots()[0].nivel == 9


def test_importar_backup_arquivo_inexistente_levanta_erro(tmp_path, monkeypatch):
  _preparar_caminhos(tmp_path, monkeypatch)

  with pytest.raises(FileNotFoundError):
    persistencia.importar_backup(tmp_path / 'nao_existe.json')


def test_importar_backup_invalido_nao_sobrescreve_save_atual(tmp_path, monkeypatch):
  _preparar_caminhos(tmp_path, monkeypatch)
  persistencia.salvar_slots([Personagem(nome='Ana'), None, None])

  arquivo_invalido = tmp_path / 'lixo.json'
  arquivo_invalido.write_text('isso não é json nenhum {{{', encoding='utf-8')

  with pytest.raises(Exception):
    persistencia.importar_backup(arquivo_invalido)

  assert persistencia.carregar_slots()[0].nome == 'Ana'  # save original intacto
