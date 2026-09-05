"""Orquestração do jogo: login/registro, criação de personagem e o loop
principal (vila -> loja/dungeon/status/etc). Tudo aqui é loop de verdade —
nada de função chamando a si mesma pra sempre feito o jogo original.
"""

import sys

from .config import Cor
from .dados.classes import CLASSES
from .dados.dungeons import DUNGEONS
from .dados.racas import RACAS
from .entrada import menu as menu_padrao
from .entrada import pedir_texto
from .interface import limpar_tela
from .modelos.personagem import Personagem
from .persistencia import carregar_contas, gerar_hash_senha, salvar_contas, verificar_senha
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


def _criar_personagem(nome, senha):
  personagem = Personagem(nome=nome, senha_hash=gerar_hash_senha(senha))

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


def _registrar(contas):
  nome = pedir_texto('Nome de usuário: -->')
  if nome in contas:
    print(f'{Cor.VERMELHO}Esse nome já está em uso.{Cor.RESET}')
    input('Enter para continuar...')
    return None
  senha = pedir_texto('Senha: -->')
  personagem = _criar_personagem(nome, senha)
  contas[nome] = personagem
  salvar_contas(contas)
  print(f'{Cor.VERDE}Conta criada com sucesso!{Cor.RESET}')
  input('Enter para continuar...')
  return personagem


def _entrar(contas):
  nome = pedir_texto('Nome de usuário: -->')
  if nome not in contas:
    print(f'{Cor.VERMELHO}Nome não encontrado.{Cor.RESET}')
    input('Enter para continuar...')
    return None
  senha = pedir_texto('Senha: -->')
  if not verificar_senha(senha, contas[nome].senha_hash):
    print(f'{Cor.VERMELHO}Senha incorreta.{Cor.RESET}')
    input('Enter para continuar...')
    return None
  return contas[nome]


def _aguardar_revive_se_necessario(personagem, contas):
  while personagem.morto:
    limpar_tela()
    if tentar_reviver(personagem):
      print(f'{Cor.VERDE}Você reviveu! Sua vida e mana foram restauradas.{Cor.RESET}')
      input('Enter para continuar...')
      return
    escolha = menu_padrao(f'{Cor.VERMELHO}Você está morto. Aguarde 5 minutos para reviver.{Cor.RESET}',
                           ['Tentar novamente', 'Salvar e sair do jogo'], com_voltar=False)
    if escolha == 1:
      salvar_contas(contas)
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
  ecrans = [loja.loja_itens, loja.loja_pocoes, loja.loja_equipamentos, loja.loja_armaduras]
  while True:
    opcoes = ['Itens/Acessórios/Comida', 'Poções', 'Equipamentos', 'Armaduras']
    escolha = menu_padrao(f'{equipamento.resumo_status(personagem)}\n\nLoja', opcoes)
    if escolha is None:
      return
    ecrans[escolha](personagem)


def _tela_dungeon(personagem, dungeon_id, contas):
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
        _aguardar_revive_se_necessario(personagem, contas)
        return
    elif acao == 'Inventário':
      _tela_inventario(personagem)
    elif acao == 'Descer de andar':
      personagem.andar_atual[dungeon_id] -= 1
    elif acao == 'Subir de andar':
      personagem.andar_atual[dungeon_id] += 1
    elif acao == 'Sair da dungeon':
      return


def _tela_vila(personagem, contas):
  while True:
    if personagem.morto:
      _aguardar_revive_se_necessario(personagem, contas)

    opcoes = ['Loja', 'Mestre de Habusken', 'Dungeon de Habusken']
    if personagem.torre_arcana_liberada:
      opcoes.append('Torre Arcana')
    opcoes += ['Personagem', 'Casa', 'Desbloquear Habilidades', 'Status',
               'Guilda', 'Curandeira', 'Saldo', 'Bancada de Trabalho',
               'Salvar Dados', 'Salvar e Sair']

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
      _tela_dungeon(personagem, 'habusken', contas)
      if 'Dragão Ancião de Habusken' in personagem.chefes_derrotados:
        personagem.torre_arcana_liberada = True
    elif acao == 'Torre Arcana':
      _tela_dungeon(personagem, 'torre_arcana', contas)
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
    elif acao == 'Salvar Dados':
      salvar_contas(contas)
      print(f'{Cor.VERDE}Dados salvos com sucesso!{Cor.RESET}')
      input('Enter para continuar...')
    elif acao == 'Salvar e Sair':
      salvar_contas(contas)
      print(f'{Cor.VERDE}Dados salvos. Até a próxima!{Cor.RESET}')
      sys.exit()


def iniciar():
  contas = carregar_contas()
  personagem = None
  while personagem is None:
    limpar_tela()
    escolha = menu_padrao('Bem-vindo ao RPG de Habusken!', ['Registrar', 'Entrar', 'Sair'], com_voltar=False)
    if escolha == 0:
      personagem = _registrar(contas)
    elif escolha == 1:
      personagem = _entrar(contas)
    else:
      print('Até a próxima!')
      return

  _aguardar_revive_se_necessario(personagem, contas)
  _tela_vila(personagem, contas)
