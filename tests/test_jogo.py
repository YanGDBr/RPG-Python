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


def test_autosalvar_nao_salva_na_primeira_chamada(monkeypatch):
  """A primeira checagem só marca o início da contagem — não faz sentido
  salvar no exato instante em que o jogador entrou na tela."""
  jogo._estado_autosave['ultimo'] = None
  chamadas_salvar = []
  monkeypatch.setattr(jogo, 'salvar_slots', lambda slots: chamadas_salvar.append(slots))
  monkeypatch.setattr(jogo.time, 'monotonic', lambda: 1000.0)

  jogo._talvez_autosalvar(Personagem(nome='teste'), slots=['s'])

  assert chamadas_salvar == []


def test_autosalvar_dispara_apos_o_intervalo_configurado(monkeypatch):
  jogo._estado_autosave['ultimo'] = None
  chamadas_salvar = []
  monkeypatch.setattr(jogo, 'salvar_slots', lambda slots: chamadas_salvar.append(slots))
  relogio = {'agora': 1000.0}
  monkeypatch.setattr(jogo.time, 'monotonic', lambda: relogio['agora'])

  personagem = Personagem(nome='teste')
  jogo._talvez_autosalvar(personagem, slots=['s'])  # marca o início
  assert chamadas_salvar == []

  relogio['agora'] += jogo.INTERVALO_AUTOSAVE_SEGUNDOS - 1
  jogo._talvez_autosalvar(personagem, slots=['s'])  # ainda não passou o suficiente
  assert chamadas_salvar == []

  relogio['agora'] += 2
  jogo._talvez_autosalvar(personagem, slots=['s'])  # agora sim
  assert chamadas_salvar == [['s']]


def test_entrar_cratera_bloqueado_antes_de_liberar():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  mensagens = []

  resultado = jogo._entrar_cratera_callback(
      personagem, mensagens.append, lambda: None, lambda: None)

  assert resultado is None
  assert any('não ir' in m for m in mensagens)


def test_entrar_cratera_liberada_retorna_sinal_de_viagem():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.cratera_vhalos_liberado = True

  resultado = jogo._entrar_cratera_callback(
      personagem, lambda *_a, **_k: None, lambda: None, lambda: None)

  assert resultado == 'cratera'


def test_derrotar_vashtar_mostra_epilogo_uma_unica_vez(monkeypatch):
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.cratera_vhalos_liberado = True

  # Simula: o jogador viaja para a Cratera, a "dungeon" (mockada) resulta na
  # derrota de Vashtar, e depois o jogador aperta Esc pra sair do mapa do mundo.
  respostas_mapa = iter(['cratera', None])
  monkeypatch.setattr(jogo.mundo, 'explorar_mapa', lambda *_a, **_k: next(respostas_mapa))

  def _fake_tela_dungeon(p, _dungeon_id, _slots):
    p.chefes_derrotados.append('Vashtar, o Rei Cinza')

  monkeypatch.setattr(jogo, '_tela_dungeon', _fake_tela_dungeon)
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  mensagens = []
  monkeypatch.setattr('builtins.print', lambda *args, **_k: mensagens.append(' '.join(str(a) for a in args)))

  jogo._tela_mapa_mundo(personagem, slots=[None, None, None])

  assert personagem.historia_concluida is True
  assert any('Vashtar' in m for m in mensagens)
