from rpg.sistemas import efeitos


def test_aplicar_e_tick_queimadura():
  lista = []
  efeitos.aplicar_efeito(lista, 'Queimadura', 2)
  assert efeitos.tem_efeito(lista, 'Queimadura')

  mensagens = []
  vida = efeitos.processar_efeitos_continuos(lista, 1000, mensagens.append, 'Monstro', vida_maxima=1000)
  assert vida == 1000 - round(1000 * efeitos.DANO_POR_TURNO['Queimadura'] / 100)
  assert lista[0]['turnos'] == 1

  vida = efeitos.processar_efeitos_continuos(lista, vida, mensagens.append, 'Monstro', vida_maxima=1000)
  assert lista == []
  assert any('acabou' in m for m in mensagens)


def test_dano_por_turno_e_percentual_da_vida_maxima_nao_valor_fixo():
  """Regressão direta do pedido: 15 de dano fixo virava irrisório contra um
  chefe de milhares de vida — agora escala com a vida máxima do alvo."""
  lista_fraco = []
  lista_tanque = []
  efeitos.aplicar_efeito(lista_fraco, 'Veneno', 1)
  efeitos.aplicar_efeito(lista_tanque, 'Veneno', 1)

  vida_fraco = efeitos.processar_efeitos_continuos(
      lista_fraco, 100, lambda *_a: None, 'Fraco', vida_maxima=100)
  vida_tanque = efeitos.processar_efeitos_continuos(
      lista_tanque, 5000, lambda *_a: None, 'Tanque', vida_maxima=5000)

  dano_fraco = 100 - vida_fraco
  dano_tanque = 5000 - vida_tanque
  assert dano_tanque > dano_fraco * 10  # escala com a vida máxima, não fixo


def test_paralisia_bloqueia_e_decrementa_ate_remover():
  lista = [{'nome': 'Paralisia', 'turnos': 1, 'valor': 0}]
  mensagens = []
  bloqueado = efeitos.verificar_paralisia(lista, mensagens.append, 'Monstro')
  assert bloqueado is True
  assert lista == []


def test_aplicar_efeito_repetido_usa_o_maior_numero_de_turnos():
  lista = []
  efeitos.aplicar_efeito(lista, 'Sangramento', 2)
  efeitos.aplicar_efeito(lista, 'Sangramento', 5)
  assert len(lista) == 1
  assert lista[0]['turnos'] == 5


def test_debuff_poder_soma_apenas_fraquezas_ativas():
  lista = [{'nome': 'Fraqueza', 'turnos': 2, 'valor': 15},
           {'nome': 'Fraqueza', 'turnos': 0, 'valor': 99},
           {'nome': 'Queimadura', 'turnos': 1, 'valor': 0}]
  assert efeitos.bonus_debuff_poder(lista) == 15
