from rpg import jogo
from rpg.dados.classes import CLASSES
from rpg.modelos.personagem import Personagem


def _fake_menu_sequencia(sequencia):
  fila = list(sequencia)

  def _fake(_titulo, _opcoes, **_kwargs):
    return fila.pop(0)

  return _fake


def test_criar_personagem_define_raca_classe_e_habilidades(monkeypatch):
  monkeypatch.setattr(jogo, 'pedir_texto', lambda *_a, **_k: 'Fulano')
  # 1ª chamada de menu = raça (índice 1 = Humano), 2ª = classe (índice 1 = Cavaleiro)
  monkeypatch.setattr(jogo, 'menu_padrao', _fake_menu_sequencia([1, 1]))
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)

  personagem = jogo._criar_personagem()

  assert personagem.nome == 'Fulano'
  assert personagem.raca == 'Humano'
  assert personagem.classe == 'Cavaleiro'
  assert personagem.habilidades_equipadas == CLASSES['Cavaleiro'].habilidades_iniciais
  assert personagem.habilidades_aprendidas == CLASSES['Cavaleiro'].habilidades_iniciais
  assert personagem.esquiva == 5  # Humano não bonifica esquiva (só Fada bonifica)
  assert personagem.local == 'vila'


def test_criar_personagem_fada_ganha_bonus_de_esquiva(monkeypatch):
  monkeypatch.setattr(jogo, 'pedir_texto', lambda *_a, **_k: 'Fadinha')
  monkeypatch.setattr(jogo, 'menu_padrao', _fake_menu_sequencia([0, 0]))  # Fada, Mago
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)

  personagem = jogo._criar_personagem()

  assert personagem.raca == 'Fada'
  assert personagem.esquiva == 5 + 6  # base + bônus da raça Fada


def test_caixa_slot_vazio_nao_quebra_com_personagem_none():
  caixa = jogo._caixa_slot(0, None)
  assert 'SLOT 1' in caixa
  assert 'vazio' in caixa


def test_caixa_slot_preenchido_mostra_nome_classe_e_nivel():
  personagem = Personagem(nome='Herói', classe='Cavaleiro', raca='Humano')
  personagem.nivel = 7
  caixa = jogo._caixa_slot(1, personagem)
  assert 'Herói' in caixa
  assert 'Cavaleiro' in caixa
  assert 'Nv.7' in caixa
