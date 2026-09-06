"""Sistema de efeitos de status: cada efeito ativo é um dict {'nome','turnos','valor'}
numa lista, em vez da string concatenada + regex do jogo original (que fazia
`status['efeito'] += 'Queimadura'` e depois usava regex pra procurar/remover —
frágil e impossível de ter dois efeitos com o mesmo prefixo).
"""

# % da vida MÁXIMA do alvo, não um valor fixo — 15 de dano fixo virava
# irrisório contra um chefe de milhares de vida e brutal contra um monstro
# fraco de 50. Contra um chefe tanque isso ainda soma bastante ao longo de
# várias rodadas, sem precisar escalar o número junto com todo o resto.
DANO_POR_TURNO = {'Queimadura': 6, 'Sangramento': 6, 'Veneno': 5}
CURA_POR_TURNO_PERCENTUAL = {'Regeneração': 8}   # % da vida máxima curada por turno
# Paralisia vem de habilidade/ataque; Atordoado vem de encher a barra de
# atordoamento (ver ATORDOAMENTO_LIMIAR) — os dois impedem agir do mesmo jeito.
EFEITOS_QUE_IMPEDEM_ACAO = {'Paralisia', 'Atordoado'}


def aplicar_efeito(lista_efeitos, nome, turnos, valor=0):
  for efeito in lista_efeitos:
    if efeito['nome'] == nome:
      efeito['turnos'] = max(efeito['turnos'], turnos)
      if valor:
        efeito['valor'] = valor
      return
  lista_efeitos.append({'nome': nome, 'turnos': turnos, 'valor': valor})


def tem_efeito(lista_efeitos, nome):
  return any(efeito['nome'] == nome and efeito['turnos'] > 0 for efeito in lista_efeitos)


def processar_efeitos_continuos(lista_efeitos, vida_atual, escrever, nome_alvo, vida_maxima=None):
  """Aplica dano de Queimadura/Sangramento/Veneno, cura de Regeneração, e
  decrementa Fraqueza/Vulnerabilidade. Paralisia é tratada à parte por
  `verificar_paralisia`, pois ela precisa ser resolvida ANTES de decidir se
  o alvo pode agir neste turno."""
  restantes = []
  for efeito in lista_efeitos:
    nome = efeito['nome']
    if nome in EFEITOS_QUE_IMPEDEM_ACAO:
      restantes.append(efeito)
      continue
    if nome in DANO_POR_TURNO:
      base = vida_maxima or vida_atual
      dano = max(1, round(base * DANO_POR_TURNO[nome] / 100))
      vida_atual = max(0, vida_atual - dano)
      escrever(f'{nome_alvo} sofre {dano} de dano por {nome}.')
    elif nome in CURA_POR_TURNO_PERCENTUAL and vida_maxima:
      cura = round(vida_maxima * CURA_POR_TURNO_PERCENTUAL[nome] / 100)
      vida_atual = min(vida_maxima, vida_atual + cura)
      escrever(f'{nome_alvo} recupera {cura} de vida por {nome}.')
    efeito['turnos'] -= 1
    if efeito['turnos'] > 0:
      restantes.append(efeito)
    else:
      escrever(f'O efeito {nome} em {nome_alvo} acabou.')
  lista_efeitos[:] = restantes
  return vida_atual


_DESCRICAO_IMPEDIMENTO = {'Paralisia': 'paralisado', 'Atordoado': 'atordoado'}


def verificar_paralisia(lista_efeitos, escrever, nome_alvo):
  """Decrementa Paralisia/Atordoado (o que estiver ativo) e diz se o alvo
  perde a vez — os dois impedem agir do mesmo jeito, só a origem muda
  (habilidade/ataque vs. barra de atordoamento cheia)."""
  for efeito in list(lista_efeitos):
    if efeito['nome'] in EFEITOS_QUE_IMPEDEM_ACAO:
      descricao = _DESCRICAO_IMPEDIMENTO.get(efeito['nome'], efeito['nome'].lower())
      escrever(f'{nome_alvo} está {descricao} e perde a vez!')
      efeito['turnos'] -= 1
      if efeito['turnos'] <= 0:
        lista_efeitos.remove(efeito)
        escrever(f'O efeito {efeito["nome"]} em {nome_alvo} acabou.')
      return True
  return False


def bonus_debuff_poder(lista_efeitos):
  return sum(efeito['valor'] for efeito in lista_efeitos
             if efeito['nome'] == 'Fraqueza' and efeito['turnos'] > 0)


def bonus_vulnerabilidade(lista_efeitos):
  return sum(efeito['valor'] for efeito in lista_efeitos
             if efeito['nome'] == 'Vulnerabilidade' and efeito['turnos'] > 0)


def bonus_marcado(lista_efeitos):
  """'Marcado' é a marca de alvo do Arqueiro — mecanicamente idêntica à
  Vulnerabilidade (bônus % de dano recebido), só que vem de uma habilidade
  específica da classe."""
  return sum(efeito['valor'] for efeito in lista_efeitos
             if efeito['nome'] == 'Marcado' and efeito['turnos'] > 0)
