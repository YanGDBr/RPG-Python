"""Exploração do mundo aberto — mesma mecânica de andar por um mapa ASCII das
dungeons (rpg/sistemas/exploracao.py), mas os pontos de interesse abrem
diálogo com NPCs ou viagem entre lugares, nunca batalha.

Cada ponto de interesse é resolvido por um "evento": uma função
`callback(personagem, escrever, aguardar, limpar) -> Optional[str]`. Retornar
`None` só mostra o que tiver que mostrar e deixa o jogador continuar andando;
retornar qualquer outra coisa (ex.: `'vethgard'`) encerra a exploração desse
mapa devolvendo esse valor pra quem chamou decidir o que fazer (trocar de
mapa, entrar numa dungeon etc.).
"""

from ..config import Cor
from ..dados.npcs import NPCS
from ..entrada import aguardar_leitura, ler_tecla
from ..interface import limpar_tela
from . import equipamento

DESLOCAMENTOS = {
  'cima': (-1, 0), 'w': (-1, 0),
  'baixo': (1, 0), 's': (1, 0),
  'esquerda': (0, -1), 'a': (0, -1),
  'direita': (0, 1), 'd': (0, 1),
}


def _encontrar_entrada(mapa):
  for y, linha in enumerate(mapa):
    x = linha.find('E')
    if x != -1:
      return [y, x]
  raise ValueError('mapa sem entrada (E)')


def _desenhar_mapa(mapa, posicao, titulo, eventos, personagem):
  linhas = [f'  {equipamento.resumo_status(personagem)}\n',
            f'  {Cor.BRANCO}{titulo}{Cor.RESET}\n']
  for y, linha in enumerate(mapa):
    celulas = []
    for x, caractere in enumerate(linha):
      if [y, x] == posicao:
        celulas.append(f'{Cor.VERDE}@{Cor.RESET}')
      elif caractere in eventos:
        celulas.append(f'{Cor.AMARELO}{caractere}{Cor.RESET}')
      elif caractere in ('.', 'E'):
        celulas.append('.')
      else:
        celulas.append(f'{Cor.CINZA}{caractere}{Cor.RESET}')
    linhas.append(' '.join(celulas))
  linhas.append('\nWASD ou setas para andar — Esc para voltar.')
  return '\n'.join(linhas)


def explorar_mapa(personagem, mapa, eventos, titulo, *, escrever=None, leitor_tecla=None,
                   limpar=None, aguardar=None):
  """Anda livremente por `mapa` até um evento sinalizar saída (retornando algo
  diferente de `None`) ou o jogador apertar Esc (retorna `None`)."""
  escrever = escrever or print
  leitor_tecla = leitor_tecla or ler_tecla
  limpar = limpar or limpar_tela
  aguardar = aguardar or aguardar_leitura

  posicao = _encontrar_entrada(mapa)
  altura, largura = len(mapa), len(mapa[0])
  celulas_andaveis = {'.', 'E'} | set(eventos)

  while True:
    limpar()
    escrever(_desenhar_mapa(mapa, posicao, titulo, eventos, personagem))
    tecla = leitor_tecla()
    if tecla == 'esc':
      return None
    deslocamento = DESLOCAMENTOS.get(tecla)
    if deslocamento is None:
      continue
    novo_y, novo_x = posicao[0] + deslocamento[0], posicao[1] + deslocamento[1]
    if not (0 <= novo_y < altura and 0 <= novo_x < largura):
      continue
    if mapa[novo_y][novo_x] not in celulas_andaveis:
      continue
    posicao = [novo_y, novo_x]
    caractere = mapa[posicao[0]][posicao[1]]
    if caractere in eventos:
      resultado = eventos[caractere](personagem, escrever, aguardar, limpar)
      if resultado is not None:
        return resultado


def mostrar_falas(nome, falas, escrever, aguardar, limpar):
  limpar()
  escrever(f'{Cor.BRANCO}{nome}{Cor.RESET}\n')
  for fala in falas:
    escrever(f'"{fala}"\n')
  aguardar()


def falar_com_npc(chave_npc):
  """Evento de mapa que abre o diálogo de um NPC e nunca encerra a
  exploração (sempre devolve `None`)."""
  def _callback(personagem, escrever, aguardar, limpar):
    npc = NPCS[chave_npc]
    mostrar_falas(npc.nome, npc.falas(personagem), escrever, aguardar, limpar)
    return None
  return _callback
