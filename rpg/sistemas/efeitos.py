"""Sistema de efeitos de status: cada efeito ativo é um dict {'nome','turnos','valor'}
numa lista, em vez da string concatenada + regex do jogo original (que fazia
`status['efeito'] += 'Queimadura'` e depois usava regex pra procurar/remover —
frágil e impossível de ter dois efeitos com o mesmo prefixo).
"""

DANO_POR_TURNO = {'Queimadura': 15, 'Sangramento': 15, 'Veneno': 12}
CURA_POR_TURNO_PERCENTUAL = {'Regeneração': 8}   # % da vida máxima curada por turno


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
    if nome == 'Paralisia':
      restantes.append(efeito)
      continue
    if nome in DANO_POR_TURNO:
      dano = DANO_POR_TURNO[nome]
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


def verificar_paralisia(lista_efeitos, escrever, nome_alvo):
  """Decrementa a Paralisia ativa (se houver) e diz se o alvo perde a vez."""
  for efeito in list(lista_efeitos):
    if efeito['nome'] == 'Paralisia':
      escrever(f'{nome_alvo} está paralisado e perde a vez!')
      efeito['turnos'] -= 1
      if efeito['turnos'] <= 0:
        lista_efeitos.remove(efeito)
        escrever(f'A paralisia de {nome_alvo} acabou.')
      return True
  return False


def bonus_debuff_poder(lista_efeitos):
  return sum(efeito['valor'] for efeito in lista_efeitos
             if efeito['nome'] == 'Fraqueza' and efeito['turnos'] > 0)


def bonus_vulnerabilidade(lista_efeitos):
  return sum(efeito['valor'] for efeito in lista_efeitos
             if efeito['nome'] == 'Vulnerabilidade' and efeito['turnos'] > 0)
