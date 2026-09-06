"""Exploração do mundo aberto — mesma ideia de andar por um mapa ASCII das
dungeons (rpg/sistemas/exploracao.py), mas os pontos de interesse abrem
diálogo com NPCs, viagem entre lugares, coleta de baú/item do chão, ou (novo)
um encontro com monstro selvagem numa célula de floresta.

Os mapas aqui são bem maiores que a tela — em vez de mostrar tudo de uma vez,
uma "câmera" (`_origem_camera`) mostra só uma janela ao redor do jogador, do
tamanho de `config.JANELA_MUNDO_*`, que rola conforme ele anda. Isso é o que
faz sentir "mundo aberto" em vez de mais uma salinha: o mapa é fixo (nunca
procedural), mas só vai aparecendo conforme o jogador se afasta da entrada.

Cada ponto de interesse "de diálogo" é resolvido por um "evento": uma função
`callback(personagem, escrever, aguardar, limpar) -> Optional[str]`. Retornar
`None` só mostra o que tiver que mostrar e deixa o jogador continuar andando;
retornar qualquer outra coisa (ex.: `'vethgard'`) encerra a exploração desse
mapa devolvendo esse valor pra quem chamou decidir o que fazer (trocar de
mapa, entrar numa dungeon etc.). Uma célula de floresta (`zonas_selvagens`) é
diferente: não é um "evento" registrado em `eventos`, é resolvida direto pelo
motor de exploração, porque ela pode abrir uma batalha de verdade.
"""

import random

from ..config import (ACOES_POR_DESGASTE_FOME_MUNDO, CHANCE_ENCONTRO_SELVAGEM, FOME_MAXIMA,
                       JANELA_MUNDO_ALTURA, JANELA_MUNDO_LARGURA, Cor)
from ..dados.monstros import MONSTROS
from ..dados.npcs import NPCS
from ..entrada import aguardar_leitura, ler_tecla, menu as menu_padrao, perguntar_sim_nao
from ..interface import limpar_tela
from . import equipamento
from .batalha import ResultadoBatalha, batalhar
from .progressao import aplicar_desgaste_fome, conceder_recompensas, verificar_morte

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


def _origem_camera(posicao, tamanho_mapa, tamanho_janela):
  """Canto onde a janela da câmera começa nesse eixo — centralizada no
  jogador, mas sem passar das bordas do mapa. Se o mapa já é menor que a
  janela (mapas de teste, mapas pequenos), a janela vira o mapa inteiro."""
  if tamanho_mapa <= tamanho_janela:
    return 0
  origem = posicao - tamanho_janela // 2
  return max(0, min(origem, tamanho_mapa - tamanho_janela))


def _desenhar_mapa(mapa, posicao, titulo, eventos, personagem, zonas_selvagens, janela):
  altura_mapa, largura_mapa = len(mapa), len(mapa[0])
  largura_janela, altura_janela = janela
  origem_y = _origem_camera(posicao[0], altura_mapa, altura_janela)
  origem_x = _origem_camera(posicao[1], largura_mapa, largura_janela)
  fim_y = min(altura_mapa, origem_y + altura_janela)
  fim_x = min(largura_mapa, origem_x + largura_janela)

  cor_fome = Cor.VERMELHO if personagem.fome <= 3 else Cor.VERDE
  linhas = [f'  {equipamento.resumo_status(personagem)}  '
            f'{cor_fome}Fome {personagem.fome}/{FOME_MAXIMA}{Cor.RESET}\n',
            f'  {Cor.BRANCO}{titulo}{Cor.RESET}\n']
  for y in range(origem_y, fim_y):
    celulas = []
    for x in range(origem_x, fim_x):
      caractere = mapa[y][x]
      if [y, x] == posicao:
        celulas.append(f'{Cor.VERDE}@{Cor.RESET}')
      elif caractere in eventos:
        celulas.append(f'{Cor.AMARELO}{caractere}{Cor.RESET}')
      elif zonas_selvagens and caractere in zonas_selvagens:
        celulas.append(f'{Cor.VERDE}{caractere}{Cor.RESET}')
      elif caractere in ('.', 'E'):
        celulas.append('.')
      else:
        celulas.append(f'{Cor.CINZA}{caractere}{Cor.RESET}')
    linhas.append(' '.join(celulas))
  linhas.append('\nWASD ou setas para andar — Esc para voltar.')
  return '\n'.join(linhas)


def _encontro_selvagem(personagem, nomes_possiveis, escrever, aguardar, limpar,
                        ler_confirmacao, ler_acao_batalha):
  nome = random.choice(nomes_possiveis)
  limpar()
  if not ler_confirmacao(f'{Cor.AMARELO}Um {nome} selvagem aparece na floresta!{Cor.RESET}\n'
                         f'Deseja lutar contra ele?'):
    escrever(f'{Cor.CINZA}Você se afasta com cuidado.{Cor.RESET}')
    aguardar()
    return

  resultado, monstro = batalhar(personagem, MONSTROS[nome], escrever=escrever,
                                 ler_acao=ler_acao_batalha, aguardar=aguardar, limpar=limpar)
  personagem.local = 'mundo'
  if resultado == ResultadoBatalha.VITORIA and not monstro.vivo:
    escrever(f'{Cor.VERDE}Você derrotou {monstro.nome}!{Cor.RESET}')
    conceder_recompensas(personagem, monstro.base, escrever)
  elif resultado == ResultadoBatalha.DERROTA:
    verificar_morte(personagem, escrever)
  elif resultado == ResultadoBatalha.MONSTRO_FUGIU:
    escrever(f'{Cor.CIANO}{monstro.nome} fugiu — nenhuma recompensa dessa vez.{Cor.RESET}')
  aguardar()


def explorar_mapa(personagem, mapa, eventos, titulo, *, escrever=None, leitor_tecla=None,
                   limpar=None, aguardar=None, zonas_selvagens=None, ler_confirmacao=None,
                   ler_acao_batalha=None, janela=None):
  """Anda livremente por `mapa` até um evento sinalizar saída (retornando algo
  diferente de `None`) ou o jogador apertar Esc (retorna `None`).

  `zonas_selvagens` (opcional): dict de caractere -> lista de nomes de
  monstro. Pisar numa dessas células tem `CHANCE_ENCONTRO_SELVAGEM` de
  chance de abrir uma batalha de verdade contra um monstro sorteado da lista.
  Cada passo de verdade também desgasta fome — bem diferente da dungeon, onde
  só desgasta ao pisar num ponto de interesse."""
  escrever = escrever or print
  leitor_tecla = leitor_tecla or ler_tecla
  limpar = limpar or limpar_tela
  aguardar = aguardar or aguardar_leitura
  ler_confirmacao = ler_confirmacao or perguntar_sim_nao
  ler_acao_batalha = ler_acao_batalha or menu_padrao
  zonas_selvagens = zonas_selvagens or {}
  janela = janela or (JANELA_MUNDO_LARGURA, JANELA_MUNDO_ALTURA)

  posicao = _encontrar_entrada(mapa)
  altura, largura = len(mapa), len(mapa[0])
  celulas_andaveis = {'.', 'E'} | set(eventos) | set(zonas_selvagens)

  while True:
    limpar()
    escrever(_desenhar_mapa(mapa, posicao, titulo, eventos, personagem, zonas_selvagens, janela))
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
    aplicar_desgaste_fome(personagem, escrever, limite_acoes=ACOES_POR_DESGASTE_FOME_MUNDO)

    caractere = mapa[posicao[0]][posicao[1]]
    if caractere in eventos:
      resultado = eventos[caractere](personagem, escrever, aguardar, limpar)
      if resultado is not None:
        return resultado
    elif caractere in zonas_selvagens:
      if random.randint(1, CHANCE_ENCONTRO_SELVAGEM) == 1:
        _encontro_selvagem(personagem, zonas_selvagens[caractere], escrever, aguardar, limpar,
                            ler_confirmacao, ler_acao_batalha)
        if personagem.morto:
          return None


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


def falar_com_npc_e_sidequest(chave_npc, sidequest_id, ler_acao=None):
  """Como `falar_com_npc`, mas depois da fala também abre a interação de
  sidequest daquele NPC (oferecer/mostrar progresso/entregar) — ver
  rpg/sistemas/sidequests.py. `ler_acao` é injetável pra teste, como todo
  resto do jogo; por padrão usa o menu de setas de verdade."""
  from . import sidequests as sistema_sidequests

  def _callback(personagem, escrever, aguardar, limpar):
    ler_acao_real = ler_acao or menu_padrao
    npc = NPCS[chave_npc]
    mostrar_falas(npc.nome, npc.falas(personagem), escrever, aguardar, limpar)
    sistema_sidequests.interagir(personagem, sidequest_id, escrever, ler_acao_real, aguardar)
    return None
  return _callback


def _ja_coletado(personagem, id_unico):
  return id_unico in personagem.mundo_coletados


def _conceder_recompensa_unica(personagem, escrever, tipo, nome, quantidade):
  if tipo == 'moedas':
    personagem.moeda_cobre += quantidade
    escrever(f'{Cor.VERDE}Você ganhou {quantidade} cobres!{Cor.RESET}')
  elif tipo == 'material':
    personagem.adicionar_material(nome, quantidade)
    escrever(f'{Cor.VERDE}Você encontrou {quantidade}x {nome}!{Cor.RESET}')
  elif tipo == 'pocao':
    personagem.pocoes[nome] = personagem.pocoes.get(nome, 0) + quantidade
    escrever(f'{Cor.VERDE}Você encontrou uma Poção de {nome}!{Cor.RESET}')
  elif tipo == 'item':
    personagem.adicionar_item(nome, quantidade)
    escrever(f'{Cor.VERDE}Você encontrou {quantidade}x {nome}!{Cor.RESET}')
  elif tipo == 'especial':
    personagem.adicionar_item_especial(nome, quantidade)
    escrever(f'{Cor.VERDE}Você encontrou algo importante: {nome}!{Cor.RESET}')


def abrir_bau(id_unico, tipo, nome, quantidade=1):
  """Evento de mapa pra um baú do mundo aberto — cada baú tem seu próprio
  `id_unico` (não dá pra reaproveitar o caractere pra isso: um mapa pode ter
  vários baús, e cada um precisa lembrar se JÁ foi aberto, separadamente)."""
  def _callback(personagem, escrever, aguardar, limpar):
    if _ja_coletado(personagem, id_unico):
      escrever(f'{Cor.CINZA}Você já abriu este baú. Está vazio.{Cor.RESET}')
      aguardar()
      return None
    escrever(f'{Cor.AMARELO}Você encontrou um baú!{Cor.RESET}')
    _conceder_recompensa_unica(personagem, escrever, tipo, nome, quantidade)
    personagem.mundo_coletados.append(id_unico)
    aguardar()
    return None
  return _callback


def pegar_item_do_chao(id_unico, tipo, nome, quantidade=1):
  """Igual a `abrir_bau`, só muda a mensagem de flavor — um item largado no
  chão em vez de guardado num baú."""
  def _callback(personagem, escrever, aguardar, limpar):
    if _ja_coletado(personagem, id_unico):
      return None
    _conceder_recompensa_unica(personagem, escrever, tipo, nome, quantidade)
    personagem.mundo_coletados.append(id_unico)
    aguardar()
    return None
  return _callback
