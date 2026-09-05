from rpg import jogo
from rpg.dados.classes import CLASSES


def _fake_menu_sequencia(sequencia):
  fila = list(sequencia)

  def _fake(_titulo, _opcoes, **_kwargs):
    return fila.pop(0)

  return _fake


def test_criar_personagem_define_raca_classe_e_habilidades(monkeypatch):
  # 1ª chamada de menu = raça (índice 1 = Humano), 2ª = classe (índice 1 = Cavaleiro)
  monkeypatch.setattr(jogo, 'menu_padrao', _fake_menu_sequencia([1, 1]))
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)

  personagem = jogo._criar_personagem('Fulano', 'senha123')

  assert personagem.raca == 'Humano'
  assert personagem.classe == 'Cavaleiro'
  assert personagem.habilidades_equipadas == CLASSES['Cavaleiro'].habilidades_iniciais
  assert personagem.habilidades_aprendidas == CLASSES['Cavaleiro'].habilidades_iniciais
  assert personagem.esquiva == 5  # Humano não bonifica esquiva (só Fada bonifica)
  assert personagem.local == 'vila'


def test_criar_personagem_fada_ganha_bonus_de_esquiva(monkeypatch):
  monkeypatch.setattr(jogo, 'menu_padrao', _fake_menu_sequencia([0, 0]))  # Fada, Mago
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)

  personagem = jogo._criar_personagem('Fadinha', 'senha123')

  assert personagem.raca == 'Fada'
  assert personagem.esquiva == 5 + 6  # base + bônus da raça Fada
