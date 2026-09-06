"""Sidequests de NPC do mundo aberto: oferecer, acompanhar progresso e
entregar — ver rpg/dados/sidequests.py pro catálogo. Bem mais simples que o
quadro de missões da guilda (não precisa sortear nada, é sempre a mesma
sidequest fixa por NPC), mas segue o mesmo espírito de "aceitar e progredir
aos poucos"."""

from ..config import Cor
from ..dados.sidequests import SIDEQUESTS


def _sidequest_ativa(personagem, sidequest_id):
  return next((s for s in personagem.sidequests_ativas if s['id'] == sidequest_id), None)


def _progresso(personagem, sidequest, ativa):
  """Devolve (já_pode_entregar, texto_de_progresso)."""
  if sidequest.tipo == 'derrotar':
    atual = ativa['progresso']
    return atual >= sidequest.quantidade, f'{atual}/{sidequest.quantidade} derrotados.'
  if sidequest.tipo == 'entregar_item':
    atual = personagem.itens_especiais.get(sidequest.alvo, 0)
    return atual >= sidequest.quantidade, f'Ainda precisa de {sidequest.quantidade}x {sidequest.alvo}.'
  if sidequest.tipo == 'entregar_material':
    atual = personagem.materiais.get(sidequest.alvo, 0)
    return atual >= sidequest.quantidade, f'Ainda precisa de {sidequest.quantidade}x {sidequest.alvo}.'
  return False, ''


def _concluir(personagem, sidequest, escrever):
  if sidequest.tipo == 'entregar_item':
    personagem.remover_item_especial(sidequest.alvo, sidequest.quantidade)
  elif sidequest.tipo == 'entregar_material':
    personagem.remover_material(sidequest.alvo, sidequest.quantidade)

  personagem.sidequests_ativas = [s for s in personagem.sidequests_ativas if s['id'] != sidequest.id]
  personagem.sidequests_completadas.append(sidequest.id)
  personagem.exp += sidequest.recompensa_exp
  personagem.moeda_cobre += sidequest.recompensa_moedas
  personagem.moedas_totais_ganhas += sidequest.recompensa_moedas

  escrever(f'{Cor.VERDE}{sidequest.texto_conclusao}{Cor.RESET}')
  escrever(f'{Cor.VERDE}Você ganhou {sidequest.recompensa_exp} de experiência e '
           f'{sidequest.recompensa_moedas} cobres!{Cor.RESET}')


def interagir(personagem, sidequest_id, escrever, ler_acao, aguardar):
  """Chamada depois da fala normal do NPC — oferece a sidequest se ainda não
  foi aceita, mostra o progresso se já foi, ou permite entregar se o
  objetivo já foi cumprido. Não faz nada se já foi completada antes."""
  sidequest = SIDEQUESTS[sidequest_id]
  if sidequest_id in personagem.sidequests_completadas:
    return

  ativa = _sidequest_ativa(personagem, sidequest_id)
  if ativa is None:
    escolha = ler_acao(f'{Cor.AMARELO}Nova sidequest: {sidequest.titulo}{Cor.RESET}\n\n'
                        f'{sidequest.descricao_oferta}', ['Aceitar', 'Recusar'])
    if escolha == 0:
      personagem.sidequests_ativas.append({'id': sidequest_id, 'progresso': 0})
      escrever(f'{Cor.VERDE}Sidequest aceita: {sidequest.titulo}{Cor.RESET}')
      aguardar()
    return

  pode_entregar, texto_progresso = _progresso(personagem, sidequest, ativa)
  if not pode_entregar:
    escrever(f'{Cor.CIANO}{sidequest.titulo}: {texto_progresso}{Cor.RESET}')
    aguardar()
    return

  escolha = ler_acao(f'{Cor.AMARELO}{sidequest.titulo}{Cor.RESET}\n\n'
                      f'Você já tem o que precisa. Entregar agora?', ['Entregar', 'Ainda não'])
  if escolha == 0:
    _concluir(personagem, sidequest, escrever)
    aguardar()


def registrar_derrota(personagem, nome_monstro, escrever):
  """Chamada de rpg/sistemas/progressao.py depois de QUALQUER monstro
  derrotado — avança o progresso de sidequests do tipo 'derrotar' ativas
  contra esse monstro, sem imprimir nada (só a entrega mostra mensagem,
  igual às missões da guilda)."""
  for ativa in personagem.sidequests_ativas:
    sidequest = SIDEQUESTS.get(ativa['id'])
    if sidequest and sidequest.tipo == 'derrotar' and sidequest.alvo == nome_monstro:
      ativa['progresso'] += 1
