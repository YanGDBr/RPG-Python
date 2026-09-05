"""Testes de regressão para o bug relatado: telas mostravam um aviso e já
voltavam pro menu (que limpa a tela) sem dar tempo de ler nada."""

from rpg.modelos.personagem import Personagem
from rpg.sistemas import cidade


def _personagem():
  return Personagem(nome='teste', classe='Cavaleiro', raca='Humano')


def test_mestre_habusken_pausa_ao_rejeitar_jogador_sem_boss_derrotado():
  personagem = _personagem()  # ainda não derrotou o Slime Gigante
  chamadas_aguardar = []

  cidade.tela_mestre_habusken(
      personagem, escrever=lambda *_a, **_k: None,
      aguardar=lambda: chamadas_aguardar.append(1))

  assert len(chamadas_aguardar) >= 1


def test_curandeira_pausa_quando_nao_tem_moedas():
  personagem = _personagem()
  personagem.moeda_cobre = 0
  chamadas_aguardar = []

  respostas_menu = iter([0, None])  # escolhe "Restaurar vida", depois sai

  def _fake_menu(_titulo, _opcoes, **_kw):
    return next(respostas_menu)

  cidade.tela_curandeira(
      personagem, escrever=lambda *_a, **_k: None, ler_acao=_fake_menu,
      entrada_texto=lambda *_a, **_k: '50',
      aguardar=lambda: chamadas_aguardar.append(1))

  assert len(chamadas_aguardar) >= 1


def test_mestre_habusken_apaga_a_tela_antes_de_pedir_a_sequencia():
  """Regressão: depois de mostrar as letras (e esperar 3s), a tela tinha que
  ser apagada antes do jogador digitar a sequência de volta — não estava."""
  personagem = _personagem()
  personagem.chefes_derrotados.append('Slime Gigante')
  personagem.moeda_cobre = 50
  eventos = []

  respostas_menu = iter([0, 1])  # treinar, depois voltar

  def _fake_menu(_titulo, _opcoes, **_kw):
    return next(respostas_menu)

  def _entrada_texto(_pergunta):
    eventos.append('pediu_sequencia')
    return ''

  cidade.tela_mestre_habusken(
      personagem, escrever=lambda *_a, **_k: None, ler_acao=_fake_menu,
      entrada_texto=_entrada_texto, esperar=lambda _s: None,
      aguardar=lambda: None, limpar=lambda: eventos.append('limpar'))

  assert eventos.count('limpar') >= 2
  assert eventos[-1] == 'pediu_sequencia'
  assert eventos[-2] == 'limpar'


def test_mestre_habusken_conta_acertos_com_resposta_separada_por_espaco(monkeypatch):
  """A resposta é digitada com `input()` de verdade (letras separadas por
  espaço, ex. 'A B C D E'), nunca com o leitor de tecla de menu — então não
  tem como o Espaço-como-Enter do menu interferir aqui."""
  personagem = _personagem()
  personagem.chefes_derrotados.append('Slime Gigante')
  personagem.moeda_cobre = 50

  letras_fixas = iter('ABCDE')
  monkeypatch.setattr(cidade.random, 'choice', lambda _seq: next(letras_fixas))

  respostas_menu = iter([0, 1])  # treinar, depois voltar

  cidade.tela_mestre_habusken(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _t, _o, **_k: next(respostas_menu),
      entrada_texto=lambda _p: 'A B C D E', esperar=lambda _s: None,
      aguardar=lambda: None, limpar=lambda: None)

  assert personagem.treinamento_habusken == 20  # 5 acertos x 4%


def test_personagem_mostra_equipamento_atual_mesmo_sem_nada_pra_trocar():
  """Regressão: depois de equipar o único acessório guardado, a tela só
  mostrava um erro genérico ('nada pra trocar') sem nunca confirmar que o
  acessório realmente ficou equipado — parecia que o equipar tinha falhado."""
  personagem = _personagem()
  personagem.acessorio_equipado = 'Bracelete da Sorte'  # já equipado, nada guardado sobrando
  telas_mostradas = []

  def _fake_menu(titulo, _opcoes, **_kw):
    telas_mostradas.append(titulo)
    return None

  cidade.tela_personagem(personagem, escrever=lambda *_a, **_k: None,
                          ler_acao=_fake_menu, aguardar=lambda: None)

  assert telas_mostradas
  assert 'Bracelete da Sorte' in telas_mostradas[0]


def test_personagem_equipa_o_unico_acessorio_guardado():
  personagem = _personagem()
  personagem.acessorios_guardados = ['Bracelete da Sorte']
  respostas = iter([0])

  def _fake_menu(_titulo, _opcoes, **_kw):
    return next(respostas, None)

  cidade.tela_personagem(personagem, escrever=lambda *_a, **_k: None,
                          ler_acao=_fake_menu, aguardar=lambda: None)

  assert personagem.acessorio_equipado == 'Bracelete da Sorte'
  assert personagem.acessorios_guardados == []


def test_status_pausa_sem_pontos_disponiveis():
  personagem = _personagem()
  personagem.pontos_status = 0
  chamadas_aguardar = []

  respostas_menu = iter([0, None])  # tenta +5 Vida máxima, depois sai

  def _fake_menu(_titulo, _opcoes, **_kw):
    return next(respostas_menu)

  cidade.tela_status(
      personagem, escrever=lambda *_a, **_k: None, ler_acao=_fake_menu,
      aguardar=lambda: chamadas_aguardar.append(1))

  assert len(chamadas_aguardar) >= 1


def test_especializacao_bloqueada_antes_do_nivel_minimo():
  personagem = _personagem()
  personagem.nivel = 10
  chamadas_aguardar = []

  cidade.tela_especializacao(
      personagem, escrever=lambda *_a, **_k: None,
      aguardar=lambda: chamadas_aguardar.append(1))

  assert personagem.especializacao == ''
  assert len(chamadas_aguardar) >= 1


def test_especializacao_escolhida_e_permanente_e_concede_habilidade():
  personagem = _personagem()  # Cavaleiro
  personagem.nivel = 30

  cidade.tela_especializacao(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _titulo, _opcoes, **_kw: 0,  # primeira opção: Paladino
      aguardar=lambda: None)

  assert personagem.especializacao == 'Paladino'
  assert 'Julgamento' in personagem.habilidades_aprendidas
  vida_apos_escolha = personagem.vida_maxima

  # escolher de novo não deve fazer nada — é permanente.
  cidade.tela_especializacao(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _titulo, _opcoes, **_kw: 1,  # tentaria escolher Berserker
      aguardar=lambda: None)

  assert personagem.especializacao == 'Paladino'
  assert personagem.vida_maxima == vida_apos_escolha


def test_ferreiro_encanta_arma_gastando_prata_e_material():
  personagem = _personagem()
  personagem.arma_equipada = 'Espada de Ferro'
  personagem.moeda_prata = 100
  personagem.adicionar_material('Cristal Arcano')

  respostas_menu = iter([0, None])  # encanta uma vez, depois sai

  cidade.tela_ferreiro(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _titulo, _opcoes, **_kw: next(respostas_menu),
      aguardar=lambda: None)

  assert personagem.encantamento_arma == 3
  assert personagem.moeda_prata < 100
  assert personagem.materiais.get('Cristal Arcano', 0) == 0


def test_ferreiro_pausa_sem_nada_pra_encantar():
  personagem = _personagem()  # sem arma/armadura equipada
  chamadas_aguardar = []

  cidade.tela_ferreiro(
      personagem, escrever=lambda *_a, **_k: None,
      aguardar=lambda: chamadas_aguardar.append(1))

  assert len(chamadas_aguardar) >= 1


def _fake_menu_sequencia(sequencia):
  fila = list(sequencia)
  return lambda _titulo, _opcoes, **_kw: fila.pop(0)


def test_guilda_so_mostra_dungeons_ja_liberadas():
  personagem = _personagem()  # nenhuma dungeon extra liberada
  opcoes_vistas = []

  def _fake_menu(_titulo, opcoes, **_kw):
    opcoes_vistas.append(opcoes)
    return None

  cidade.tela_guilda(personagem, escrever=lambda *_a, **_k: None,
                      ler_acao=_fake_menu, aguardar=lambda: None, _quadros_cache={})

  assert opcoes_vistas[0] == ['Dungeon de Habusken']


def test_guilda_mostra_dungeons_liberadas_conforme_progresso():
  personagem = _personagem()
  personagem.torre_arcana_liberada = True
  opcoes_vistas = []

  def _fake_menu(_titulo, opcoes, **_kw):
    opcoes_vistas.append(opcoes)
    return None

  cidade.tela_guilda(personagem, escrever=lambda *_a, **_k: None,
                      ler_acao=_fake_menu, aguardar=lambda: None, _quadros_cache={})

  assert opcoes_vistas[0] == ['Dungeon de Habusken', 'Torre Arcana']


def test_quadro_de_andares_mostra_so_ate_o_maior_andar_ja_visitado():
  personagem = _personagem()
  personagem.maior_andar_visitado['habusken'] = 2
  opcoes_vistas = []

  def _fake_menu(_titulo, opcoes, **_kw):
    opcoes_vistas.append(opcoes)
    return None

  # 1ª chamada = escolhe "Dungeon de Habusken"; 2ª (dentro de _tela_quadro_andares)
  # já é a que queremos inspecionar.
  respostas = iter([0, None, None])
  cidade.tela_guilda(personagem, escrever=lambda *_a, **_k: None,
                      ler_acao=lambda t, o, **kw: (opcoes_vistas.append(o), next(respostas))[1],
                      aguardar=lambda: None, _quadros_cache={})

  assert len(opcoes_vistas[1]) == 2  # Andar 1 e Andar 2, nunca o 3


def test_equipar_e_desequipar_missao_no_quadro():
  personagem = _personagem()
  # dungeon -> andar 1 -> equipa missão 1 -> desequipa a mesma -> sai de tudo
  ler_acao = _fake_menu_sequencia([0, 0, 0, 0, None, None, None])

  cidade.tela_guilda(personagem, escrever=lambda *_a, **_k: None,
                      ler_acao=ler_acao, aguardar=lambda: None, _quadros_cache={})

  assert personagem.missoes_ativas == []


def test_nao_deixa_equipar_terceira_missao():
  personagem = _personagem()
  # dungeon -> andar 1 -> equipa missão 1, missão 2, tenta missão 3 -> sai de tudo
  ler_acao = _fake_menu_sequencia([0, 0, 0, 1, 2, None, None, None])
  mensagens = []

  cidade.tela_guilda(personagem, escrever=mensagens.append,
                      ler_acao=ler_acao, aguardar=lambda: None, _quadros_cache={})

  assert len(personagem.missoes_ativas) == 2
  assert any('já tem' in m for m in mensagens)


def test_renovar_quadro_cobra_moedas():
  personagem = _personagem()
  saldo_antes = personagem.moeda_cobre
  # dungeon -> andar 1 -> "Renovar quadro" (índice 3, após as 3 missões) -> sai de tudo
  ler_acao = _fake_menu_sequencia([0, 0, 3, None, None, None])

  cidade.tela_guilda(personagem, escrever=lambda *_a, **_k: None,
                      ler_acao=ler_acao, aguardar=lambda: None, _quadros_cache={})

  assert personagem.moeda_cobre == saldo_antes - 100
