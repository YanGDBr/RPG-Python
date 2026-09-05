from rpg import persistencia
from rpg.modelos.personagem import Personagem


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
