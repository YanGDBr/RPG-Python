"""Orquestração do jogo: seleção de save slot, criação de personagem e o loop
principal (vila -> loja/dungeon/status/etc). Tudo aqui é loop de verdade —
nada de função chamando a si mesma pra sempre feito o jogo original.
"""

import sys

from .config import Cor
from .dados.classes import CLASSES
from .dados.dungeons import DUNGEONS
from .dados.especializacoes import NIVEL_MINIMO_ESPECIALIZACAO
from .dados.racas import RACAS
from .entrada import menu as menu_padrao
from .entrada import pedir_texto, perguntar_sim_nao
from .interface import barra, cabecalho, limpar_tela, ljust_visivel
from .modelos.personagem import Personagem
from .persistencia import carregar_slots, salvar_slots
from .sistemas import cidade, equipamento, exploracao, inventario, loja
from .sistemas.progressao import tentar_reviver

HISTORIA_INICIAL = """Você era um cidadão de uma cidade no interior do Brasil, um policial respeitado. Sua
última investigação era de uma criança desaparecida — você a encontrou, mas o sequestrador ameaçava jogá-la
de um prédio. Para impedir isso, você se sacrificou junto com o sequestrador, caindo de um prédio de 10
andares. Vendo que você foi um bom policial, Deus o reencarnou em um mundo de fantasia, com magia, monstros
e habilidades, para que aproveitasse a vida do jeito que quisesse. Nesse mundo existem dungeons cuja origem
é misteriosa — surgiram há 1800 anos, num mundo que vive por volta do período medieval.

Você acorda em um corpo adulto, numa casa simples, com uma mochila contendo 100 cobres, um pouco
de comida e documentos de identidade. Decide se tornar um aventureiro e desvendar o mistério das dungeons.
"""

EPILOGO = """Com o Kraken Ancestral derrotado, as águas do Abismo Submerso finalmente se aquietam. Entre os
destroços flutuantes, você entende: O Arquiteto não criou as dungeons por acaso — elas eram um teste, uma
peneira para separar quem seria digno de herdar o que restou de um mundo antigo. Você não sabe se essa
resposta é um fim ou um começo, mas sabe que sobreviveu a tudo que esse mundo pôde jogar contra você.

A história que te trouxe até aqui, de um policial que caiu de um prédio, termina como uma lenda entre os
aventureiros de Habusken. A sua jornada, porém, continua — sempre há mais uma dungeon, mais um mistério,
mais um andar abaixo do último."""

_ICONE_CLASSE = {'Mago': '(*)', 'Cavaleiro': '[X]', 'Arqueiro': '}=>'}
_LARGURA_CAIXA = 50


def _linha_caixa(texto):
  return f'|{ljust_visivel(" " + texto, _LARGURA_CAIXA - 2)}|'


def _caixa_slot(indice, personagem):
  borda = '+' + '-' * (_LARGURA_CAIXA - 2) + '+'
  if personagem is None:
    linhas = [
      borda,
      _linha_caixa(f'{Cor.BRANCO}SLOT {indice + 1}{Cor.RESET}'),
      _linha_caixa(f'{Cor.CINZA}(vazio — escolha para criar um personagem){Cor.RESET}'),
      borda,
    ]
    return '\n'.join(linhas)

  icone = _ICONE_CLASSE.get(personagem.classe, '?')
  vida_max = equipamento.vida_maxima_efetiva(personagem)
  linhas = [
    borda,
    _linha_caixa(f'{Cor.BRANCO}SLOT {indice + 1}{Cor.RESET}'),
    _linha_caixa(f'{icone} {personagem.nome} — {personagem.raca} {personagem.classe}, Nv.{personagem.nivel}'),
    _linha_caixa(f'Vida: {barra(personagem.vida, vida_max, largura=22, cor=Cor.VERMELHO)}'),
    borda,
  ]
  return '\n'.join(linhas)


def _tela_selecionar_slot(slots):
  titulo = f'{cabecalho("RPG DE HABUSKEN")}\n\nEscolha um save slot:'
  opcoes = [_caixa_slot(i, slots[i]) for i in range(len(slots))] + ['Sair do jogo']
  return menu_padrao(titulo, opcoes, com_voltar=False)


def _criar_personagem():
  nome = pedir_texto('Nome do personagem: -->')
  personagem = Personagem(nome=nome)

  limpar_tela()
  print(HISTORIA_INICIAL)
  input('\nAperte Enter para continuar...')

  nomes_racas = list(RACAS.keys())
  while True:
    escolha = menu_padrao('Escolha sua raça', nomes_racas + ['Ver informações'], com_voltar=False)
    if escolha == len(nomes_racas):
      limpar_tela()
      print('\n'.join(f'{r.nome}: {r.descricao}' for r in RACAS.values()))
      input('Enter para continuar...')
      continue
    personagem.raca = nomes_racas[escolha]
    raca = RACAS[personagem.raca]
    if raca.bonus_tipo == 'esquiva':
      personagem.esquiva += raca.valor
    elif raca.bonus_tipo == 'vida':
      personagem.vida_maxima = round(personagem.vida_maxima * (1 + raca.valor / 100))
      personagem.vida = personagem.vida_maxima
    if raca.contrapartida_tipo == 'mana':
      personagem.mana_maxima = round(personagem.mana_maxima * (1 - raca.contrapartida_valor / 100))
      personagem.mana = personagem.mana_maxima
    break

  nomes_classes = list(CLASSES.keys())
  while True:
    escolha = menu_padrao('Escolha sua classe', nomes_classes + ['Ver informações'], com_voltar=False)
    if escolha == len(nomes_classes):
      limpar_tela()
      print('\n'.join(f'{c.nome}: {c.descricao}' for c in CLASSES.values()))
      input('Enter para continuar...')
      continue
    personagem.classe = nomes_classes[escolha]
    break

  classe = CLASSES[personagem.classe]
  personagem.habilidades_aprendidas = list(classe.habilidades_iniciais)
  personagem.habilidades_equipadas = list(classe.habilidades_iniciais)
  personagem.local = 'vila'
  return personagem


def _aguardar_revive_se_necessario(personagem, slots):
  while personagem.morto:
    limpar_tela()
    if tentar_reviver(personagem):
      print(f'{Cor.VERDE}Você reviveu! Sua vida e mana foram restauradas.{Cor.RESET}')
      input('Enter para continuar...')
      return
    escolha = menu_padrao(f'{Cor.VERMELHO}Você está morto. Aguarde 5 minutos para reviver.{Cor.RESET}',
                           ['Tentar novamente', 'Salvar e sair do jogo'], com_voltar=False)
    if escolha == 1:
      salvar_slots(slots)
      print('Dados salvos.')
      sys.exit()


def _tela_inventario(personagem):
  while True:
    nomes_pocoes = [nome for nome, qtd in personagem.pocoes.items() if qtd > 0]
    nomes_itens = [nome for nome, qtd in personagem.inventario.items() if qtd > 0]
    opcoes = [f'Poção de {nome} x{personagem.pocoes[nome]}' for nome in nomes_pocoes]
    opcoes += [f'{nome} x{personagem.inventario[nome]}' for nome in nomes_itens]
    if not opcoes:
      limpar_tela()
      print(f'{Cor.CIANO}Seu inventário de itens está vazio.{Cor.RESET}')
      input('Enter para continuar...')
      return
    escolha = menu_padrao(f'{equipamento.resumo_status(personagem)}\n\nInventário', opcoes)
    if escolha is None:
      return
    if escolha < len(nomes_pocoes):
      inventario.usar_pocao(personagem, nomes_pocoes[escolha], em_batalha=False, escrever=print)
    else:
      inventario.usar_item_consumivel(personagem, nomes_itens[escolha - len(nomes_pocoes)], print)
    input('Enter para continuar...')


def _tela_loja(personagem):
  ecrans = [loja.loja_itens, loja.loja_pocoes, loja.loja_equipamentos, loja.loja_armaduras,
            loja.loja_ofertas_do_dia]
  while True:
    opcoes = ['Itens/Acessórios/Comida', 'Poções', 'Equipamentos', 'Armaduras',
              f'{Cor.AMARELO}Ofertas do Dia{Cor.RESET}']
    escolha = menu_padrao(f'{equipamento.resumo_status(personagem)}\n\nLoja', opcoes)
    if escolha is None:
      return
    ecrans[escolha](personagem)


def _tela_dungeon(personagem, dungeon_id, slots):
  dungeon = DUNGEONS[dungeon_id]
  while True:
    andar_num = personagem.andar_atual[dungeon_id]
    andar = dungeon.andares[andar_num - 1]

    opcoes = ['Explorar', 'Inventário']
    if andar_num > 1:
      opcoes.append('Descer de andar')
    pode_subir = (andar.chefe in personagem.chefes_derrotados and andar_num < len(dungeon.andares))
    if pode_subir:
      opcoes.append('Subir de andar')
    opcoes.append('Sair da dungeon')

    titulo = (f'{equipamento.resumo_status(personagem)}\n\n'
              f'{dungeon.nome} — Andar {andar_num}: {Cor.BRANCO}{andar.nome}{Cor.RESET}\n'
              f'{andar.faixa_nivel}\nChefe deste andar: {andar.chefe}')
    escolha = menu_padrao(titulo, opcoes, com_voltar=False)
    acao = opcoes[escolha]

    if acao == 'Explorar':
      exploracao.explorar(personagem, dungeon_id)
      if personagem.morto:
        _aguardar_revive_se_necessario(personagem, slots)
        return
    elif acao == 'Inventário':
      _tela_inventario(personagem)
    elif acao == 'Descer de andar':
      personagem.andar_atual[dungeon_id] -= 1
    elif acao == 'Subir de andar':
      personagem.andar_atual[dungeon_id] += 1
    elif acao == 'Sair da dungeon':
      return


def _tela_vila(personagem, slots):
  while True:
    if personagem.morto:
      _aguardar_revive_se_necessario(personagem, slots)

    opcoes = ['Loja', 'Mestre de Habusken', 'Dungeon de Habusken']
    if personagem.torre_arcana_liberada:
      opcoes.append('Torre Arcana')
    if personagem.abismo_submerso_liberado:
      opcoes.append('Abismo Submerso')
    opcoes += ['Personagem', 'Casa', 'Desbloquear Habilidades', 'Status',
               'Guilda', 'Curandeira', 'Saldo', 'Bancada de Trabalho', 'Ferreiro']
    if personagem.nivel >= NIVEL_MINIMO_ESPECIALIZACAO:
      opcoes.append('Especialização')
    opcoes += ['Estatísticas', 'Mapa de Progresso', 'Salvar Dados', 'Salvar e Sair']

    cor_fome = Cor.VERMELHO if personagem.fome <= 3 else Cor.VERDE
    titulo = (f'{Cor.BRANCO}Vila Habusken — {personagem.nome}{Cor.RESET}\n'
              f'{equipamento.resumo_status(personagem)}  '
              f'{cor_fome}Fome {personagem.fome}/10{Cor.RESET}')
    escolha = menu_padrao(titulo, opcoes, com_voltar=False)
    acao = opcoes[escolha]

    if acao == 'Loja':
      _tela_loja(personagem)
    elif acao == 'Mestre de Habusken':
      cidade.tela_mestre_habusken(personagem)
    elif acao == 'Dungeon de Habusken':
      _tela_dungeon(personagem, 'habusken', slots)
      if 'Dragão Ancião de Habusken' in personagem.chefes_derrotados:
        personagem.torre_arcana_liberada = True
    elif acao == 'Torre Arcana':
      _tela_dungeon(personagem, 'torre_arcana', slots)
      if 'O Arquiteto' in personagem.chefes_derrotados:
        personagem.abismo_submerso_liberado = True
    elif acao == 'Abismo Submerso':
      _tela_dungeon(personagem, 'abismo_submerso', slots)
      if 'Kraken Ancestral' in personagem.chefes_derrotados and not personagem.historia_concluida:
        personagem.historia_concluida = True
        limpar_tela()
        print(EPILOGO)
        input('\nAperte Enter para continuar...')
    elif acao == 'Personagem':
      cidade.tela_personagem(personagem)
    elif acao == 'Casa':
      cidade.tela_casa(personagem)
    elif acao == 'Desbloquear Habilidades':
      cidade.tela_desbloquear_habilidades(personagem)
    elif acao == 'Status':
      cidade.tela_status(personagem)
    elif acao == 'Guilda':
      cidade.tela_guilda(personagem)
    elif acao == 'Curandeira':
      cidade.tela_curandeira(personagem)
    elif acao == 'Saldo':
      cidade.tela_bau(personagem)
    elif acao == 'Bancada de Trabalho':
      cidade.tela_crafting(personagem)
    elif acao == 'Ferreiro':
      cidade.tela_ferreiro(personagem)
    elif acao == 'Especialização':
      cidade.tela_especializacao(personagem)
    elif acao == 'Estatísticas':
      cidade.tela_estatisticas(personagem)
    elif acao == 'Mapa de Progresso':
      cidade.tela_mapa_progresso(personagem)
    elif acao == 'Salvar Dados':
      salvar_slots(slots)
      print(f'{Cor.VERDE}Dados salvos com sucesso!{Cor.RESET}')
      input('Enter para continuar...')
    elif acao == 'Salvar e Sair':
      salvar_slots(slots)
      print(f'{Cor.VERDE}Dados salvos. Até a próxima!{Cor.RESET}')
      sys.exit()


def iniciar():
  slots = carregar_slots()
  personagem = None

  while personagem is None:
    limpar_tela()
    escolha = _tela_selecionar_slot(slots)
    if escolha == len(slots):
      print('Até a próxima!')
      return
    indice = escolha

    if slots[indice] is None:
      personagem = _criar_personagem()
      slots[indice] = personagem
      salvar_slots(slots)
      print(f'{Cor.VERDE}Personagem criado com sucesso!{Cor.RESET}')
      input('Enter para continuar...')
    else:
      limpar_tela()
      acao = menu_padrao(_caixa_slot(indice, slots[indice]),
                          ['Continuar', 'Apagar personagem', 'Voltar'], com_voltar=False)
      if acao == 0:
        personagem = slots[indice]
      elif acao == 1:
        nome_antigo = slots[indice].nome
        if perguntar_sim_nao(f'Tem certeza que quer apagar {nome_antigo}? Isso não pode ser desfeito.'):
          slots[indice] = None
          salvar_slots(slots)
          print(f'{Cor.AMARELO}{nome_antigo} foi apagado.{Cor.RESET}')
          input('Enter para continuar...')

  _aguardar_revive_se_necessario(personagem, slots)
  _tela_vila(personagem, slots)
