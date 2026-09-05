from rpg import persistencia
from rpg.modelos.personagem import Personagem


def test_hash_senha_nao_e_texto_plano_e_verifica_corretamente():
  hash_gerado = persistencia.gerar_hash_senha('minhasenha')
  assert hash_gerado != 'minhasenha'
  assert persistencia.verificar_senha('minhasenha', hash_gerado)
  assert not persistencia.verificar_senha('senhaerrada', hash_gerado)


def test_round_trip_salvar_e_carregar(tmp_path, monkeypatch):
  caminho_falso = tmp_path / 'contas.json'
  monkeypatch.setattr(persistencia, 'ARQUIVO_SAVE', caminho_falso)

  personagem = Personagem(nome='Ana', senha_hash=persistencia.gerar_hash_senha('123'))
  personagem.nivel = 5
  personagem.inventario['Perfume Anti-Monstro'] = 2
  personagem.habilidades_equipadas = ['Investida', 'Corte Fatal', 'Espada Mágica']

  persistencia.salvar_contas({'Ana': personagem})
  assert caminho_falso.exists()

  carregadas = persistencia.carregar_contas()
  assert carregadas['Ana'].nivel == 5
  assert carregadas['Ana'].inventario['Perfume Anti-Monstro'] == 2
  assert carregadas['Ana'].habilidades_equipadas == ['Investida', 'Corte Fatal', 'Espada Mágica']
  assert persistencia.verificar_senha('123', carregadas['Ana'].senha_hash)


def test_carregar_sem_arquivo_devolve_dicionario_vazio(tmp_path, monkeypatch):
  monkeypatch.setattr(persistencia, 'ARQUIVO_SAVE', tmp_path / 'nao_existe.json')
  assert persistencia.carregar_contas() == {}
