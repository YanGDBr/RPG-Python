from rpg.sistemas import efeitos


def test_aplicar_e_tick_queimadura():
  lista = []
  efeitos.aplicar_efeito(lista, 'Queimadura', 2)
  assert efeitos.tem_efeito(lista, 'Queimadura')

  mensagens = []
  vida = efeitos.processar_efeitos_continuos(lista, 100, mensagens.append, 'Monstro')
  assert vida == 100 - efeitos.DANO_POR_TURNO['Queimadura']
  assert lista[0]['turnos'] == 1

  vida = efeitos.processar_efeitos_continuos(lista, vida, mensagens.append, 'Monstro')
  assert lista == []
  assert any('acabou' in m for m in mensagens)


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
