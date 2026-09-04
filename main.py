import pickle
import os
from time import sleep
from unidecode import unidecode
from random import randint, choice
from datetime import datetime
from re import search, sub
from math import trunc
from threading import Thread

if os.name == 'nt':
  import msvcrt as _msvcrt
  _msvcrt_getch_original = _msvcrt.getch
  def _msvcrt_getch_decodificado():
    return _msvcrt_getch_original().decode('latin-1')
  _msvcrt.getch = _msvcrt_getch_decodificado

from getkey import getkey, keys


def s(comando):
  if comando == 'clear':
    os.system('cls' if os.name == 'nt' else 'clear')
  else:
    os.system(comando)


class cores():
  blue = '\033[1;34m'
  red = '\033[1;31m'
  green = '\033[1;32m'
  negrito = '\033[;1m'
  yellow = '\033[1;93m'
  pink = '\033[1;95m'


now = datetime.now()
batalhaativa = 'nao'
danototal = 0
andar = 0
nomen = ''
player = ''
inva = cores.red + 'Você insiriu algo invalido' + cores.negrito


class conta():

  def __init__(self, nome, senha):
    self.senha = senha
    self.nome = nome
    self.coins = {'moedacobre': 200, 'moedaprata': 0, 'moedaouro': 0}
    self.vida = {'vida': 100, 'vidamax': 100}
    self.mana = {'mana': 100, 'manamax': 100}
    self.bossderrotado = {'Slime Gigante': 'nao', 'Goblin Xama': 'nao'}
    self.poder = 0
    self.poderbuff = 0
    self.esquiva = 10
    self.morto = 'nao'
    self.treinamento = {'habusken': 0}
    self.status = {
      'efeito': '',
      'turnosqueimadura': 0,
      'turnosparalisia': 0,
      'turnossangramento': 0,
      'debuffpoder': 0
    }
    self.eten = 'nao'
    self.poçao = {'Vida': 0, 'Mana': 0, 'Esquiva': 0, 'Poder': 0}
    self.habs = {}
    self.buffequipamento = 0
    self.equipamento = {}
    self.equipado = {
      'acessorio': {
        'nome': 'Nenhum', 'desc': 'Nada'
      },
      'armadura': {
        'nome': 'Nenhum', 'desc': 'Nada'
      },
      'arma': {
        'nome': ' '
      }
    }
    self.itens = {'itens': {}, 'acessorio': {}}
    self.itenusado = {'Efeito': {}}
    self.armadura = {}
    self.no = 1
    self.missao = {
      'monstro': '',
      'quantia': 0,
      'quantiamatar': 999,
      'recompensa': {
        'coins': 0,
        'coinstipo': '',
        'exp': 0
      }
    }
    self.umavez = 1
    self.reviver = ''
    self.nivel = 1
    self.exp = {'exp': 0, 'expup': self.nivel * 50}
    self.casa = {
      'fome': 10,
      'descansar': self.nivel,
      'descansados': 0,
      'comida': {
        'Bife': 4,
        'Frango': 3,
        'Arroz': 3
      }
    }
    self.statpoint = 0
    self.raca = 'a'
    self.classe = ''
    self.hab1 = ''
    self.hab2 = ''
    self.hab3 = ''
    self.lugar = 'inicio'


try:
  pickle_in = open("usuarios.pickle", "rb")
  usuarios = pickle.load(pickle_in)
  pickle_in.close()
except (FileNotFoundError, EOFError):
  usuarios = {}
  pickle_out = open("usuarios.pickle", "wb")
  pickle.dump(usuarios, pickle_out)
  pickle_out.close()


def registrar(nome, senha):
  if nome in usuarios:
    print('Este nome ja foi registrado')
    sleep(1.5)
    s('clear')
    teste()
  else:
    usuarios[nome] = conta(nome, senha)
    pickle_out = open("usuarios.pickle", "wb")
    pickle.dump(usuarios, pickle_out)
    pickle_out.close()
    print('Conta criada com sucesso!!')
    sleep(1.5)
    s('clear')
    teste()


def logar():
  while True:
    nome = input('Nome:')
    senha = input('Senha:')
    if nome not in usuarios:
      print('\nNome não registrado')
    elif senha != usuarios[nome].senha:
      print('\nSenha Invalida')
    else:
      logado(nome)
      break


class Player:

  def __init__(self, nomer):
    self.nome = usuarios[nomer].nome
    self.senha = usuarios[nomer].senha
    self.vida = usuarios[nomer].vida
    self.lugar = usuarios[nomer].lugar
    self.casa = usuarios[nomer].casa
    self.no = usuarios[nomer].no
    self.mana = usuarios[nomer].mana
    self.poder = usuarios[nomer].poder
    self.poderbuff = usuarios[nomer].poderbuff
    self.esquiva = usuarios[nomer].esquiva
    self.status = usuarios[nomer].status
    self.bossderrotado = usuarios[nomer].bossderrotado
    self.nivel = usuarios[nomer].nivel
    self.morto = usuarios[nomer].morto
    self.umavez = usuarios[nomer].umavez
    self.treinamento = usuarios[nomer].treinamento
    self.eten = usuarios[nomer].eten
    self.itenusado = usuarios[nomer].itenusado
    self.poçao = usuarios[nomer].poçao
    self.habs = usuarios[nomer].habs
    self.buffequipamento = usuarios[nomer].buffequipamento
    self.equipamento = usuarios[nomer].equipamento
    self.equipado = usuarios[nomer].equipado
    self.itens = usuarios[nomer].itens
    self.armadura = usuarios[nomer].armadura
    self.reviver = usuarios[nomer].reviver
    self.exp = usuarios[nomer].exp
    self.statpoint = usuarios[nomer].statpoint
    self.raca = usuarios[nomer].raca
    self.coins = usuarios[nomer].coins
    self.classe = usuarios[nomer].classe
    self.hab1 = usuarios[nomer].hab1
    self.hab2 = usuarios[nomer].hab2
    self.hab3 = usuarios[nomer].hab3
    self.missao = usuarios[nomer].missao


def fome():
    player.casa['fome'] -= 1
    print(
      f'A Fome do seu personagem aumentou, nivel de comida: {player.casa["fome"]*10}%'
    )
    if player.casa['fome'] <= 0:
      print(
        'Você morreu por desnutrição'
      )
      sleep(3)
      player.vida['vida'] = 0
      verificarmorto()
    elif player.casa['fome'] <= 5:
      print(
        'A fome do seu persongem está em situação critica, por causa disso terá um debuff de 10% em Poder'
      )
      player.status['efeito'] += 'Poder'
      player.status['debuffpoder'] += 10
      sleep(5)


esquivaantiga = 0


def logado(nome):
  global nomen, esquivaantiga, now
  nomen = nome
  print(f'Bem Vindo {nome}')
  print('Carregando Dados...')
  Player(nome)
  sla()
  esquivaantiga = player.esquiva
  sleep(5)
  s('clear')
  now = datetime.now()
  if player.morto == 'sim':
    if now.day - player.reviver['dia'] >= 1:
      player.morto = 'nao'
      player.vida['vida'] = player.vida['vidamax']
      player.mana['mana'] = player.mana['manamax']
      print('Voce reviveu, logue novamente em sua conta')
      sleep(1.5)
    else:
      if now.hour - player.reviver['hora'] >= 1:
        player.vida['vida'] = player.vida['vidamax']
        player.mana['mana'] = player.mana['manamax']
        player.morto = 'nao'
        print('Voce reviveu, logue novamente em sua conta')
        sleep(1.5)
      else:
        if now.minute - player.reviver['minuto'] >= 5:
          player.vida['vida'] = player.vida['vidamax']
          player.mana['mana'] = player.mana['manamax']
          player.morto = 'nao'
          print('Voce reviveu, logue novamente em sua conta')
          sleep(1.5)
        else:
          print(
            'Voce esta morto ainda, por favor espere ate voce poder reviver para logar'
          )
          sleep(1.5)
  else:
    Thread(target=fome, daemon=True).start()
    if player.lugar == 'vila habusken':
      vilahabusken()
    elif player.lugar == 'inicio':
      inicio()


class Monstros:

  def __init__(self):
    self.habusken = self.Habusken()

  class Habusken:

    def __init__(self):
      self.andar1habusken = self.Andar1Habusken()
      self.andar2habusken = self.Andar2Habusken()
      self.andar3habusken = self.Andar3Habusken()
      self.andar4habusken = self.Andar4Habusken()
      self.andar5habusken = self.Andar5Habusken()

    class Andar1Habusken:

      def __init__(self):
        self.Slime = {
          'nome': 'Slime',
          'vida': 50,
          'atkmin': 5,
          'atkmax': 8,
          'nivel': 1,
          'drops': {
            'expmin': 10,
            'expmax': 15,
            'coinsmin': 5,
            'coinsmax': 15,
            'coinstipo': 'moedacobre',
            'itens': ''
          },
          'desc': {
            'desc1': 'O Slime dá uma cabeçada em você',
            'desc2': 'O Slime ataca sua perna o fazendo cair no chão',
            'tipodesc1': 'Ataque',
            'tipodesc2': 'Ataque'
          },
          'status': '',
          'turnosqueimadura': 0,
          'turnossangramento': 0,
          'turnosparalisia': 0,
          'turnosveneno': 0
        }
        self.Kobold = {
          'nome': 'Kobold',
          'vida': 60,
          'atkmin': 8,
          'atkmax': 10,
          'nivel': 3,
          'drops': {
            'expmin': 16,
            'expmax': 25,
            'coinsmin': 10,
            'coinsmax': 20,
            'coinstipo': 'moedacobre',
            'itens': ''
          },
          'desc': {
            'desc1': 'O Kobold te corta com uma adaga',
            'desc2': 'O Kobold perfura sua costela',
            'tipodesc1': 'Ataque',
            'tipodesc2': 'Ataque'
          },
          'status': '',
          'turnosqueimadura': 0,
          'turnossangramento': 0,
          'turnosparalisia': 0,
          'turnosveneno': 0
        }
        self.Lobo = {
          'nome': 'Lobo',
          'vida': 65,
          'atkmin': 10,
          'atkmax': 13,
          'nivel': 4,
          'drops': {
            'expmin': 18,
            'expmax': 28,
            'coinsmin': 13,
            'coinsmax': 23,
            'coinstipo': 'moedacobre',
            'itens': ''
          },
          'desc': {
            'desc1': 'O Lobo dá uma investida e te morde ferozmente',
            'desc2': 'O Lobo te ataca com suas garras',
            'tipodesc1': 'Ataque',
            'tipodesc2': 'Ataque'
          },
          'status': '',
          'turnosqueimadura': 0,
          'turnossangramento': 0,
          'turnosparalisia': 0,
          'turnosveneno': 0
        }
        self.SlimeGigante = {
          'nome': 'Slime Gigante',
          'vida': 150,
          'atkmin': 20,
          'atkmax': 25,
          'nivel': 10,
          'drops': {
            'expmin': 30,
            'expmax': 50,
            'coinsmin': 20,
            'coinsmax': 35,
            'coinstipo': 'moedacobre',
            'itens': ''
          },
          'desc': {
            'desc1': 'O Slime gigante pula e te esmaga',
            'desc2':
            'O Slime Gigante dá uma rapida investida e te joga contra a parede',
            'tipodesc1': 'Ataque',
            'tipodesc2': 'Ataque'
          },
          'status': '',
          'turnosqueimadura': 0,
          'turnossangramento': 0,
          'turnosparalisia': 0,
          'turnosveneno': 0
        }

    class Andar2Habusken:

      def __init__(self):
        self.Goblin = {
          'nome': 'Goblin',
          'vida': 80,
          'atkmin': 8,
          'atkmax': 13,
          'nivel': 5,
          'drops': {
            'expmin': 20,
            'expmax': 30,
            'coinsmin': 15,
            'coinsmax': 30,
            'coinstipo': 'moedacobre',
            'itens': ''
          },
          'desc': {
            'desc1':
            'O Goblin desaparece na escuridão e furtivamente lhe golpeia por trás',
            'desc2':
            'O Goblin tenta perfutar sua perna mas só consegue de raspão',
            'tipodesc1': 'Ataque',
            'tipodesc2': 'Ataque'
          },
          'status': '',
          'turnosqueimadura': 0,
          'turnossangramento': 0,
          'turnosparalisia': 0,
          'turnosveneno': 0
        }

        self.Esqueleto = {
          'nome': 'Esqueleto',
          'vida': 100,
          'atkmin': 13,
          'atkmax': 17,
          'nivel': 8,
          'drops': {
            'expmin': 25,
            'expmax': 35,
            'coinsmin': 20,
            'coinsmax': 35,
            'coinstipo': 'moedacobre',
            'itens': ''
          },
          'desc': {
            'desc1': 'O Esqueleto atira uma flecha na sua perna',
            'desc2': 'O Esqueleto atira uma rapidá flecha em seu braço',
            'tipodesc1': 'Ataque',
            'tipodesc2': 'Ataque'
          },
          'status': '',
          'turnosqueimadura': 0,
          'turnossangramento': 0,
          'turnosparalisia': 0,
          'turnosveneno': 0
        }

        self.KoboldMago = {
          'nome': 'Kobold Mago',
          'vida': 110,
          'atkmin': 17,
          'atkmax': 20,
          'nivel': 10,
          'drops': {
            'expmin': 30,
            'expmax': 40,
            'coinsmin': 25,
            'coinsmax': 50,
            'coinstipo': 'moedacobre',
            'itens': ''
          },
          'desc': {
            'desc1': 'O Kobold Mago conjura uma bola de fogo em você',
            'desc2': 'O Kobold Mago conjura um missil magico em sua direção',
            'tipodesc1': 'Ataque e Efeito Debuff',
            'tipodesc2': 'Ataque'
          },
          'Efeitodesc1': 'Queimadura',
          'status': '',
          'turnosqueimadura': 0,
          'turnossangramento': 0,
          'turnosparalisia': 0,
          'turnosveneno': 0
        }

        self.GoblinXama = {
          'nome': 'Goblin Xamã',
          'vida': 170,
          'atkmin': 30,
          'atkmax': 40,
          'nivel': 15,
          'drops': {
            'expmin': 50,
            'expmax': 80,
            'coinsmin': 40,
            'coinsmax': 80,
            'coinstipo': 'moedacobre',
            'itens': ''
          },
          'desc': {
            'desc1': 'O Goblin Xamã aumenta sua própria vida',
            'desc2':
            'O Goblin Xamã conjura espinhos flamejantes em sua direção',
            'tipodesc1': 'Efeito Buff',
            'tipodesc2': 'Ataque e Efeito Debuff'
          },
          'Efeitodesc1': 'Cura',
          'Efeitodesc2': 'Queimadura',
          'status': '',
          'turnosqueimadura': 0,
          'turnossangramento': 0,
          'turnosparalisia': 0,
          'turnosveneno': 0
        }

    class Andar3Habusken:
      pass

    class Andar4Habusken:
      pass

    class Andar5Habusken:
      pass


monstroatual = ''


def sla():
  global nomen, player
  player = Player(nomen)


def verificarmorto():
  global player, now
  if player.vida['vida'] <= 0:
    player.morto = 'sim'
    reviver = {'hora': now.hour, 'minuto': now.minute + 5, 'dia': now.day}
    player.reviver = reviver
    s('clear')
    print('Você morreu, voce ira reviver daqui a 5 minutos')
    salvardados()
    print('Dados salvos, logue novamente depois de 5 minutos')
    sleep(5)
    exit()


def salvardados():
  global nomen, player
  usuarios[nomen].vida = player.vida
  usuarios[nomen].lugar = player.lugar
  usuarios[nomen].mana = player.mana
  usuarios[nomen].no = player.no
  usuarios[nomen].casa = player.casa
  usuarios[nomen].poder = player.poder
  usuarios[nomen].poderbuff = player.poderbuff
  usuarios[nomen].esquiva = player.esquiva
  usuarios[nomen].nivel = player.nivel
  usuarios[nomen].status = player.status
  usuarios[nomen].treinamento = player.treinamento
  usuarios[nomen].eten = player.eten
  usuarios[nomen].poçao = player.poçao
  usuarios[nomen].habs = player.habs
  usuarios[nomen].buffequipamento = player.buffequipamento
  usuarios[nomen].equipamento = player.equipamento
  usuarios[nomen].equipado = player.equipado
  usuarios[nomen].itenusado = player.itenusado
  usuarios[nomen].itens = player.itens
  usuarios[nomen].armadura = player.armadura
  usuarios[nomen].bossderrotado = player.bossderrotado
  usuarios[nomen].exp = player.exp
  usuarios[nomen].statpoint = player.statpoint
  usuarios[nomen].missao = player.missao
  usuarios[nomen].umavez = player.umavez
  usuarios[nomen].morto = player.morto
  usuarios[nomen].reviver = player.reviver
  usuarios[nomen].raca = player.raca
  usuarios[nomen].coins = player.coins
  usuarios[nomen].classe = player.classe
  usuarios[nomen].hab1 = player.hab1
  usuarios[nomen].hab2 = player.hab2
  usuarios[nomen].hab3 = player.hab3

  pickle_out = open('usuarios.pickle', 'wb')
  pickle.dump(usuarios, pickle_out)
  pickle_out.close()


def lugarsalvo():
  global player, batalhaativa, monstroatual, antelugar
  if player.lugar == 'vila habusken':
    vilahabusken()
  if player.lugar == 'habusken':
    dungeonhabusken()
  if player.lugar == 'batalha':
    if monstroatual['vida'] <= 0:
      if antelugar == 'habusken':
        dungeonhabusken()
    else:
      batalhar(monstroatual)


def verificarmonstromorto(monstro):
  global player, batalhaativa, danoextra, poçaopoderusada, poçaoesquivausada, antelugar
  if monstro['vida'] <= 0:
    fome()
    s('clear')
    batalhaativa = 'nao'
    player.esquiva = esquivaantiga
    danoextra = 0
    poçaopoderusada = 'nao'
    poçaoesquivausada = 'nao'
    player
    if monstro['nome'] == 'Slime Gigante':
      player.bossderrotado['Slime Gigante'] = 'sim'
    elif monstro['nome'] == 'Goblin Xamã':
      player.bossderrotado['Goblin Xama'] = 'sim'
    s('clear')
    print(f'Voce matou o {monstro["nome"]}')
    sleep(2)

    ex = randint(monstro['drops']['expmin'], monstro['drops']['expmax'])
    co = randint(monstro['drops']['coinsmin'], monstro['drops']['coinsmax'])
    kk = 1
    while True:
      try:
        if player.itenusado['Efeito']['bufftipo' + str(kk)] == 'Drop':
          ex = ex + ex * player.itenusado['Efeito']['buff' + kk] / 100
          co = co + co * player.itenusado['Efeito']['buff' + kk] / 100
          ex = trunc(ex)
          co = trunc(co)
          print(
            'Recompensas Aumentadas devido ao iten usado antes da morte do monstro, efeito do item se passou'
          )
          del player.itenusado['Efeito']['buff' + str(kk)]
          del player.itenusado['Efeito']['bufftipo' + str(kk)]
          sleep(3)
          s('clear')
          break
        else:
          kk += 1
      except:
        break
    if player.raca['raca'] == 'Elfo':
      ex = ex + ex * player.raca['valor'] / 100
      ex = trunc(ex)
      print('Bonus de experiencia devido a raça')
      sleep(3)
      s('clear')
    if monstro['drops']['coinstipo'] == 'moedacobre':
      player.coins['moedacobre'] += co
      print(f'Voce ganhou {co} de Moedas de Cobre')
    player.exp['exp'] += ex
    print(f'Voce ganhou {ex} de Exp')
    sleep(1.5)
    if player.exp['exp'] >= player.exp['expup']:
      player.statpoint += 3
      player.nivel += 1
      player.exp['exp'] -= player.exp['expup']
      player.exp['expup'] = player.nivel * 50
      print('Voce evoluiu de nivel, ganhou 3 pontos de status')

    sleep(2.5)
    s('clear')
    verificarmissao(monstro)
    s('clear')
    lugarsalvo()


def monstroatacar(monstro):
  global player
  a = [monstro['desc']['desc1'], monstro['desc']['desc2']]
  des = choice(a)
  if des == monstro['desc']['desc1']:
    topzao = monstro['desc']['tipodesc1']
    try:
      efect = monstro['Efeitodesc1']
    except:
      pass
  elif des == monstro['desc']['desc2']:
    topzao = monstro['desc']['tipodesc2']
    try:
      efect = monstro['Efeitodesc2']
    except:
      pass
  if monstro['vida'] <= 0:
    verificarmonstromorto(monstro)
  else:
    if search('Queimadura', monstro['status']) != None:
      if monstro['turnosqueimadura'] >= 1:
        monstro['turnosqueimadura'] -= 1
        monstro['vida'] -= 15
        s('clear')
        print(
          cores.red +
          f'O {monstro["nome"]} sofre com a Queimadura, perdendo 15 de vida' +
          cores.negrito)
        sleep(1.5)
        s('clear')
      else:
        print(cores.red + 'A Queimadura do Monstro Parou' + cores.negrito)
        sleep(1.5)
        s('clear')
        monstro['status'] = sub('Queimadura', '', monstro['status'])
    if search('Sangramento', monstro['status']) != None:
      if monstro['turnossangramento'] >= 1:
        monstro['turnossangramento'] -= 1
        monstro['vida'] -= 15
        s('clear')
        print(
          cores.red +
          f'O {monstro["nome"]} sofre com o Sangramento, perdendo 15 de vida' +
          cores.negrito)
        sleep(1.5)
        s('clear')
      else:
        print(cores.red + 'O Sangramento do monstro parou' + cores.negrito)
        sleep(1.5)
        s('clear')
        monstro['status'] = sub('Sangramento', '', monstro['status'])
    if search('Veneno', monstro['status']) != None:
      if monstro['turnosveneno'] >= 1:
        monstro['turnosveneno'] -= 1
        monstro['vida'] -= 15
        s('clear')
        print(cores.red +
              f'O {monstro["nome"]} sofre com o Veneno, perdendo 15 de vida' +
              cores.negrito)
        sleep(1.5)
        s('clear')
      else:
        print(cores.red + 'O Envenenamento do monstro parou' + cores.negrito)
        sleep(1.5)
        s('clear')
        monstro['status'] = sub('Veneno', '', monstro['status'])
    if monstro['vida'] <= 0:
      verificarmonstromorto(monstro)

    else:
      if search('Paralisia', monstro['status']) == None:
        if randint(1, player.esquiva) != 2:
          if search('Ataque', topzao) != None:
            dan = randint(monstro['atkmin'], monstro['atkmax'])
            player.vida['vida'] -= dan
            print(cores.yellow + des + cores.negrito)
            print(cores.red + f'Causando {dan} de Dano em você' +
                  cores.negrito)
            sleep(3.5)
            s('clear')
            if topzao == 'Ataque e Efeito Debuff':
              print(f'O {monstro["nome"]} causou {efect} em você')
              if efect == 'Queimadura':
                player.status['efeito'] += 'Queimadura'
                player.status['turnosqueimadura'] = 1
            batalhar(monstro)
          else:
            if topzao == 'Efeito Buff':
              print(cores.pink + des + cores.negrito)
              sleep(3.5)
              s('clear')
              if efect == 'Cura':
                monstro['vida'] += 25
              batalhar(monstro)
        else:
          s('clear')
          print(cores.pink + 'Voce desvia do ataque do monstro' +
                cores.negrito)
          sleep(2.5)
          s('clear')
          batalhar(monstro)
      else:
        if monstro['turnosparalisia'] >= 1:
          monstro['turnosparalisia'] -= 1
          if monstro['turnosparalisia'] == 0:
            print('A Paralisia acabou')
            monstro['status'] = sub('Paralisia', '', monstro['status'])
          s('clear')
          print(cores.yellow + 'Monstro esta paralisado' + cores.negrito)
          sleep(1.5)
          s('clear')
          batalhar(monstro)


danoextra = 0


def atacar(monstro, habilidade):
  global player, danoextra
  player.poderbuff = player.poder * 5
  player.buffequipamento = player.equipado['arma']['buff']
  if search('Ataque', habilidade['tipo']) != None:
    danototal = habilidade['dano'] * player.poderbuff / 100
    danototal += habilidade['dano']
    danototal = danototal + danototal * player.buffequipamento / 100
    danototal = danototal + danototal * danoextra / 100
    if player.raca['raca'] == 'Humano':
      danototal = danototal + danototal * 10 / 100 
    if player.eten == 'sim':
      danototal = danototal + danototal * 30 / 100
    if search('Poder', player.status['efeito']) != None:
      danototal = danototal - danototal * player.status['debuffpoder'] / 100
      print(
        f'Você recebeu um debuff de {player.status["debuffpoder"]}% em Poder')
      sleep(3)
      s('clear')

  if randint(1, 10) != 4:
    if habilidade['tipo'] == 'Multiplo Ataque':
      acertos = randint(habilidade['quantiamin'], habilidade['quantiamax'])
      danototal = habilidade['dano'] * acertos
      danototal += danototal * player.poderbuff / 100
      if player.raca['raca'] == 'Humano':
        danototal += danototal * 10 / 100
      monstro['vida'] -= danototal
      s('clear')
      print(
        cores.blue +
        f'Você {habilidade["desc"]}, Acertando {acertos} delas, Causando {danototal} de dano ao {monstro["nome"]}'
        + cores.negrito)
      sleep(2.5)

    elif search('Ataque', habilidade['tipo']) != None:
      monstro['vida'] -= danototal
      s('clear')
      print(
        cores.blue +
        f'Você {habilidade["desc"]}, Causando {danototal} de dano ao {monstro["nome"]}'
        + cores.negrito)
      sleep(2.5)
    if search('Efeito', habilidade['tipo']) != None:
      monstro['status'] += habilidade['Efeito']
      if habilidade['Efeito'] == 'Queimadura':
        monstro['turnosqueimadura'] = habilidade['turnos']
      elif habilidade['Efeito'] == 'Sangramento':
        monstro['turnossangramento'] = habilidade['turnos']
      elif habilidade['Efeito'] == 'Paralisia':
        monstro['turnosparalisia'] = habilidade['turnos']
      elif habilidade['Efeito'] == 'Veneno':
        monstro['turnosveneno'] = habilidade['turnos']
      s('clear')
      print(cores.green + f'Você causou {habilidade["Efeito"]} no monstro' +
            cores.negrito)
      sleep(2.5)
      s('clear')
    monstroatacar(monstro)

  else:
    s('clear')
    print(cores.yellow + 'Você infelizmente erra' + cores.negrito)
    sleep(1.5)
    s('clear')
    monstroatacar(monstro)


def batalhar(monstro):
  global player, batalhaativa, danototal
  player.lugar = 'batalha'
  if player.vida['vida'] <= 0:
    verificarmorto()
  if search('Queimadura', player.status['efeito']) != None:
    if player.status['turnosqueimadura'] > 0:
      player.vida['vida'] -= 15
      player.status['turnosqueimadura'] -= 1
      print(cores.red + 'Você sofre 15 de dano por causa da Queimadura' +
            cores.negrito)
      sleep(2.5)
      s('clear')
    else:
      player.status['efeito'] = sub('Queimadura', '', player.status['efeito'])
      print('A Queimadura acabou')
      sleep(1.5)

  if search('Sangramento', player.status['efeito']) != None:
    if player.status['turnossangramento'] > 0:
      player.vida['vida'] -= 15
      player.status['turnossangramento'] -= 1
      print(cores.red + 'Você sofre 15 de dano por causa do Sangramento' +
            cores.negrito)
      sleep(2.5)
      s('clear')
    else:
      player.status['efeito'] = sub('Sangramento', '', player.status['efeito'])
      print('O Sangramento acabou')
      sleep(1.5)

  if search('Veneno', player.status['efeito']) != None:
    if player.status['turnosveneno'] > 0:
      player.vida['vida'] -= 15
      player.status['turnosveneno'] -= 1
      print(cores.red + 'Você sofre 15 de dano por causa do Veneno' +
            cores.negrito)
      sleep(2.5)
      s('clear')
    else:
      player.status['efeito'] = sub('Veneno', '', player.status['efeito'])
      print('O Veneno acabou')
      sleep(1.5)
  if player.vida['vida'] <= 0:
    verificarmorto()

  else:
    batalhaativa = 'sim'
    player.poderbuff = player.poder * 5
    player.hab1['cooldown'] -= 1
    player.hab2['cooldown'] -= 1
    player.hab3['cooldown'] -= 1

    if player.umavez == 1:
      player.umavez = 0
      print(cores.red + f'''
Você entrou em batalha contra um {monstro['nome']}''' + cores.negrito)
      player.hab1['cooldown'] = 0
      player.hab2['cooldown'] = 0
      player.hab3['cooldown'] = 0
    if player.hab1['cooldown'] < 0:
      player.hab1['cooldown'] = 0
    if player.hab2['cooldown'] < 0:
      player.hab2['cooldown'] = 0
    if player.hab3['cooldown'] < 0:
      player.hab3['cooldown'] = 0
    bata = input(cores.negrito + f'''
            Batalha
    {monstro['nome']} Vida: {monstro['vida']}

(1) Usar {player.hab1['nome']}
Mana: {player.hab1['mana']}
Dano: {player.hab1['dano']*player.poderbuff/100 + player.hab1['dano']}
Cooldown: {player.hab1['cooldown']} Turnos

(2) Usar {player.hab2['nome']}
Mana: {player.hab2['mana']}
Dano: {player.hab2['dano']*player.poderbuff/100 + player.hab2['dano']}
Cooldown: {player.hab2['cooldown']} Turnos

(3) Usar {player.hab3['nome']}
Mana: {player.hab3['mana']} 
Dano: {player.hab3['dano']*player.poderbuff/100 + player.hab3['dano']}
Cooldown: {player.hab3['cooldown']} Turnos

(4) Tentar fugir
(5) Pular vez
(6) Itens

    {cores.red}Vida atual: {player.vida['vida']}{cores.negrito}
    {cores.blue}Mana Atual: {player.mana['mana']}{cores.negrito}
    
              -->''')
    if bata == '1' and player.mana['mana'] >= player.hab1['mana']:
      if player.hab1['cooldown'] <= 0:
        player.hab1['cooldown'] = player.hab1['cooldownmax']
        player.mana['mana'] -= player.hab1['mana']
        player.mana['mana'] = player.mana['manamax'] * \
            10/100 + player.mana['mana']
        if player.mana['mana'] > player.mana['manamax']:
          player.mana['mana'] = player.mana['manamax']
        atacar(monstro, player.hab1)
      else:
        s('clear')
        print('Habilidade em cooldown')
        sleep(3)
        s('clear')
        batalhar(monstro)
    elif bata == '2' and player.mana['mana'] >= player.hab2['mana']:
      if player.hab2['cooldown'] <= 0:
        player.hab2['cooldown'] = player.hab2['cooldownmax']
        player.mana['mana'] -= player.hab2['mana']
        player.mana['mana'] = player.mana['manamax'] * \
            10/100 + player.mana['mana']
        if player.mana['mana'] > player.mana['manamax']:
          player.mana['mana'] = player.mana['manamax']
        atacar(monstro, player.hab2)
      else:
        s('clear')
        print('Habilidade em cooldown')
        sleep(3)
        s('clear')
        batalhar(monstro)  
    elif bata == '3' and player.mana['mana'] >= player.hab3['mana']:
      if player.hab3['cooldown'] <= 0:
        player.hab3['cooldown'] = player.hab3['cooldownmax']
        player.mana['mana'] -= player.hab3['mana']
        player.mana['mana'] = player.mana['manamax'] * \
            10/100 + player.mana['mana']
        if player.mana['mana'] > player.mana['manamax']:
          player.mana['mana'] = player.mana['manamax']
        atacar(monstro, player.hab3)
      else:
        s('clear')
        print('Habilidade em cooldown')
        sleep(3)
        s('clear')
        batalhar(monstro)
    elif bata == '4':
      if randint(1, 5) == 3:
        batalhaativa = 'nao'
        s('clear')
        print('Voce foge com sucesso')
        sleep(1.5)
        s('clear')
        lugarsalvo()
      else:
        s('clear')
        print('Voce não consegue fugir')
        sleep(1.5)
        s('clear')
        monstroatacar(monstro)
    elif bata == '5':
      player.mana['mana'] = player.mana['manamax'] * \
          10/100 + player.mana['mana']
      if player.mana['mana'] > player.mana['manamax']:
        player.mana['mana'] = player.mana['manamax']
      s('clear')
      print('Voce pula a vez')
      sleep(1.5)
      s('clear')
      monstroatacar(monstro)
    elif bata == '6':
      s('clear')
      inventario()
    else:
      print(cores.blue+ 'Você insiriu algo invalido ou não tem mana o suficiente' + cores.negrito)
      sleep(1.5)
      s('clear')
      batalhar(monstro)


# Criar player.treinamento, player.eten, player.poçao, player.buffequipamento, player.equipamento, player.equipado, player.itens, Personagem em Vila Habusken
# Criar player.armadura, danoextra
poçaoesquivausada = 'nao'
poçaopoderusada = 'nao'
danoextra = 0


def inventario():
  global player, poçaoesquivausada, poçaopoderusada, batalhaativa, esquivaantiga
  poçaovida = ''
  poçaomana = ''
  poçaoesquiva = ''
  poçaopoder = ''
  print('''
        Inventario

(1) Voltar        
''')
  iten = 2
  iten1 = 1
  iten2 = 1
  iten3 = 1
  while True:
    try:
      print(
        f'\n        ({iten})\nNome: {player.itens["itens"]["iten" + str(iten1)]["nome"]}\nQuantidade: {player.itens["itens"]["iten"+str(iten1)]["quantia"]}\nDescrição:{player.itens["itens"]["iten"+str(iten1)]["desc"]}\n'
      )
      iten1 += 1
      iten += 1
      iten2 += 1
      iten3 += 1
    except:
      break
  if player.poçao['Vida'] >= 1:
    print(f'\n     ({iten})\nPoção de Vida:{player.poçao["Vida"]}\n')
    iten += 1
    poçaovida = iten
    iten2 += 1
    iten3 += 1
  if player.poçao['Mana'] >= 1:
    print(f'\n     ({iten})\nPoção de Mana:{player.poçao["Mana"]}\n')
    iten += 1
    poçaomana = iten
    iten2 += 1
    iten3 += 1
  if player.poçao['Esquiva'] >= 1:
    print(f'\n     ({iten})\nPoção de Esquiva:{player.poçao["Esquiva"]}\n')
    iten += 1
    poçaoesquiva = iten
    iten2 += 1
    iten3 += 1
  if player.poçao['Poder'] >= 1:
    print(f'\n    ({iten})\nPoção de Poder:{player.poçao["Poder"]}\n')
    iten += 1
    poçaopoder = iten
    iten2 += 1
    iten3 += 1
  if player.casa["comida"]['Bife'] >= 1:
    print(f'\n     ({iten})\nBifes:{player.casa["comida"]["Bife"]}\n')
    iten += 1
    iten3 += 1
  if player.casa["comida"]['Arroz'] >= 1:
    print(
      f'\n     ({iten})\nPotes de Arroz: {player.casa["comida"]["Arroz"]}\n')
    iten += 1
    iten3 += 1
  if player.casa["comida"]['Frango'] >= 1:
    print(f'\n     ({iten})\nFrango: {player.casa["comida"]["Frango"]}\n')
    iten += 1
    iten3 += 1

  inv = input('\n           -->')
  inv = sub(' ', '', inv)
  certo = inv.isnumeric()
  if certo == False:
    s('clear')
    print('Você digitou algo invalido')
    sleep(2)
    s('clear')
    inventario()
  else:
    inv = int(inv)
  if inv <= 0:
    s('clear')
    print('Você digitou algo invalido')
    sleep(2)
    s('clear')
    inventario()
  else:
    if inv > 1 and inv <= iten1:
      tipo = 'item'
    elif inv > iten1 and inv <= iten2:
      tipo = 'poçao'
    elif inv > iten2 and inv <= iten3:
      tipo = 'comida'
    if inv == 1:
      s('clear')
      lugarsalvo()
    else:

      ha = 1
      try:
        if tipo == 'item':
          inv -= 1
          if player.itens['itens']['iten' + str(inv)]['bufftipo'] == 'Monstro':
            while True:
              try:
                if player.itenusado['Efeito']['bufftipo' + str(ha)] == 'Anti Monstro':
                  s('clear')
                  print(
                    'Você está com Efeito de Anti-Monstro, então não é possivel usar este item'
                  )
                  sleep(5)
                  s('clear')
                  inventario()
                  break
                else:
                  ha += 1
              except:
                break

            player.itenusado['Efeito']['bufftipo' + str(ha)] = 'Monstro'
            player.itenusado['Efeito']['buff' + str(ha)] = player.itens['itens']['iten' + str(inv)]['buff']
            player.itens['itens']['iten' + str(inv)]['quantia'] -= 1
            if player.itens['itens']['iten' + str(inv)]['quantia'] == 0:
              del player.itens['itens']['iten' + str(inv)]

          elif player.itens['itens']['iten' + str(inv)]['bufftipo'] == 'Anti Monstro':
            while True:
              try:
                if player.itenusado['Efeito']['bufftipo' + str(ha)] == 'Monstro':
                  s('clear')
                  print(
                    'Você está com Efeito de Monstro, então não é possivel usar este item'
                  )
                  sleep(5)
                  s('clear')
                  inventario()
                  break
                else:
                  ha += 1
              except:
                break
            player.itenusado['Efeito']['bufftipo' + str(ha)] = 'Anti Monstro'
            player.itenusado['Efeito']['buff' + str(ha)] = player.itens['itens']['iten' + str(inv)]['buff']
            player.itens['itens']['iten' + str(inv)]['quantia'] -= 1
            if player.itens['itens']['iten' + str(inv)]['quantia'] == 0:
              del player.itens['itens']['iten' + str(inv)]
          elif player.itens['itens']['iten' + str(inv)]['bufftipo'] == 'Drop':
            while True:
              try:
                if player.itenusado['Efeito']['bufftipo' + str(ha)] == 'sarsafa':
                  pass
                ha += 1
              except:
                break
            player.itenusado['Efeito']['bufftipo' + str(ha)] = 'Drop'
            player.itenusado['Efeito']['buff' + str(ha)] = player.itens['itens']['iten' + str(inv)]['buff']
            player.itens['itens']['iten' + str(inv)]['quantia'] -= 1
            if player.itens['itens']['iten' + str(inv)]['quantia'] == 0:
              del player.itens['itens']['iten' + str(inv)]
        elif tipo == 'poçao':
          if inv == poçaovida:
            player.poçao['Vida'] -= 1
            player.vida['vida'] += 60
            if player.vida['vida'] > player.vida['vidamax']:
              player.vida['vida'] = player.vida['vidamax']
          elif inv == poçaomana:
            player.poçao['Mana'] -= 1
            player.mana['mana'] += 60
            if player.mana['mana'] > player.mana['manamax']:
              player.mana['mana'] = player.mana['manamax']
          elif inv == poçaoesquiva:
            if batalhaativa == 'sim':
              if poçaoesquivausada == 'nao':
                esquivaantiga = player.esquiva
                player.esquiva -= 2
                player.poçao['Esquiva'] -= 1
                poçaoesquivausada = 'sim'
              else:
                s('clear')
                print('Você ja usou esta poção')
                sleep(3)
                s('clear')
                inventario()
            else:
              s('clear')
              print('Esta poção só pode ser usada em batalha')
              sleep(3)
              s('clear')
              inventario()
          elif inv == poçaopoder:
            if batalhaativa == 'sim':
              if poçaopoderusada == 'nao':
                danoextra += 10
                player.poçao['Poder'] -= 1
                poçaopoderusada = 'sim'
              else:
                s('clear')
                print('Você ja usou esta poção')
                sleep(3)
                s('clear')
                inventario()
            else:
              s('clear')
              print('Esta poção só pode ser usada em batalha')
              sleep(3)
              s('clear')
              inventario()
        elif tipo == 'comida':
          s('clear')
          print('Você só pode comer na sua casa')
          sleep(2)
          s('clear')
          inventario()

      except:
        pass


def avatar():
  global player
  print(f'''
         Personagem

 Acessorio Equipado: {player.equipado['acessorio']['nome']}
Efeito: {player.equipado['acessorio']['desc']}

 Armadura Equipada: {player.equipado['armadura']['nome']}
Buffs: {player.equipado['armadura']['desc']}

 Arma equipada: {player.equipado['arma']['nome']}
Buffs: {player.equipado['arma']['buff']}% de Poder


(1) Voltar

        Equipaveis
 ''')
  top = 2
  top1 = 1
  top2 = 1
  top3 = 1
  while True:
    try:
      print(
        f'\n          ({top})\nNome: {player.equipamento["equipamento" + str(top1)]["nome"]}\nBuffs: {player.equipamento["equipamento"+ str(top1)]["buff"]}% de Poder\n'
      )
      top += 1
      top1 += 1
    except:
      break
  while True:
    try:
      print(
        f'\n          ({top})\nNome: {player.itens["acessorio"]["iten" + str(top2)]["nome"]}\nEfeitos: {player.itens["acessorio"]["iten"+ str(top2)]["desc"]}\n'
      )
      top2 += 1
      top += 1
    except:
      break
  while True:
    try:
      print(
        f'\n          ({top})\nNome: {player.armadura["armadura" + str(top3)]["nome"]}\nBuffs: {player.armadura["armadura"+ str(top3)]["desc"]}\n'
      )
      top += 1
      top3 += 1
    except:
      break

  top1fim = top1
  top2fim = top1 + (top2 - 1)
  top3fim = top2fim + (top3 - 1)

  try:
    avata = int(input('\n        -->'))
    if avata == 1:
      s('clear')
      lugarsalvo()
      return
    if avata > 1 and avata <= top1fim:
      tipo = 'equipamento'
    elif avata > top1fim and avata <= top2fim:
      tipo = 'acessorio'
    elif avata > top2fim and avata <= top3fim:
      tipo = 'armadura'
    else:
      s('clear')
      print(inva)
      sleep(2)
      s('clear')
      avatar()
      return
    if tipo == 'equipamento':
      if avata in range(2, top1fim + 1):
        avata -= 1
        antigo = player.equipado['arma']
        player.equipado['arma'] = player.equipamento['equipamento' + str(avata)]
        player.equipamento['equipamento' + str(avata)] = antigo
    elif tipo == 'acessorio':
      if avata in range(top1fim + 1, top2fim + 1):
        a = 0
        for i in range(top1fim + 1, avata + 1):
          a += 1
        antigo = player.equipado['acessorio']
        player.equipado['acessorio'] = player.itens['acessorio']['iten' + str(a)]
        if antigo['nome'] == 'Nenhum':
          pass
        else:
          player.itens['acessorio']['iten' + str(a)] = antigo
    elif tipo == 'armadura':
      if avata in range(top2fim + 1, top3fim + 1):
        a = 0
        for i in range(top2fim + 1, avata + 1):
          a += 1
        antigo = player.equipado['armadura']
        player.equipado['armadura'] = player.armadura['armadura' + str(a)]
        if antigo['nome'] == 'Nenhum':
          pass
        else:
          player.armadura['armadura' + str(a)] = antigo
    s('clear')
    print('Equipado com sucesso')
    sleep(3)
    s('clear')
    avatar()

  except:
    s('clear')
    print('Você digitou algo invalido')
    sleep(2)
    s('clear')
    avatar()


def lojaitens():
  global player
  iten = input('''
      Loja de Itens/Acessorios/Comida
(1) Voltar

                                        ACESSORIOS

      (2)                 |         (3)             |      (4)
Colar do Labirinto        | Pulseira Sagrada        | Anel de Fogo
90 Moedas de Cobre        | 100 Moedas de Cobre     | 130 Moedas de Cobre
                          |                         | 
Aumenta um pouco a chance | Aumenta a Mana e a Vida | Comece a partida colocando
de achar a sala do boss   | Em 25                   | seu inimigo com o efeito 
                          |                         | Queimadura por 3 turnos


                                   COMIDA
       (5)          |    (6)             |    (7)                                                             
Pote de Arroz       | Bife               | Frango                               
20 Moedas de Cobre  | 20 Moedas de Cobre | 20 Moedas de Cobre                                                              
                    |                    |                                                      
Diminui a fome      | Diminui a fome     | Diminui a fome


                                   Itens

       (8)              |     (9)                 |     (10)                                                                                                                                    
Perfume Anti-Monstro    | Perfume Monstro         | Drop Buffer                                                                        
50 Moedas de Cobre      | 50 Moedas de cobre      | 150 Moedas de Cobre                                                                                 
                        |                         |                                                                   
Diminui a chance de ser | Aumenta a chance de ser | Aumenta a chance de dropar                                                                          
atacado por um monstro  | atacado por um monstro  | itens e aumenta o drop de coins
                        |                         | e exp                                    





                          -->''')
  if iten == '1':
    s('clear')
    loja()
  elif iten == '2' and player.coins['moedacobre'] >= 90:
    sla = 1
    s('clear')
    player.coins['moedacobre'] -= 90
    while True:
      try:
        if player.itens['acessorio']['iten' + str(sla)] == 'sla2142141':
          pass
        sla += 1
      except:
        player.itens['acessorio']['iten' + str(sla)] = {
          'nome': 'Colar do Labirinto',
          'bufftipo': 'Boss',
          'buff': 5,
          'desc': 'Aumenta um pouco a chance de achar a sala do boss'
        }
        break
    print('Você comprou um Colar do Labirinto')
  elif iten == '3' and player.coins['moedacobre'] >= 100:
    sla = 1
    s('clear')
    player.coins['moedacobre'] -= 100
    while True:
      try:
        if player.itens['acessorio']['iten' + str(sla)] not in player.itens:
          pass
        sla += 1
      except:
        player.itens['acessorio']['iten' + str(sla)] = {
          'nome': 'Pulseira Sagrada',
          'bufftipo': 'Mana Vida',
          'buff': 25,
          'desc': 'Aumenta a mana e a vida em 25'
        }
        break

    print('Você comprou uma Pulseira Sagrada')
  elif iten == '4' and player.coins['moedacobre'] >= 130:
    sla = 1
    s('clear')
    player.coins['moedacobre'] -= 130
    while True:
      try:
        if player.itens['acessorio']['iten' + str(sla)] not in player.itens:
          pass
        sla += 1
      except:
        player.itens['acessorio']['iten' + str(sla)] = {
          'nome':
          'Anel de Fogo',
          'bufftipo':
          'Queimadura',
          'buff':
          3,
          'desc':
          'Quando começar uma batalha o inimigo irá ficar com o Efeito Queimadura por 3 turnos'
        }
        break
    print('Você comprou um Anel de Fogo')
  elif iten == '5' and player.coins['moedacobre'] >= 20:
    player.coins['moedacobre'] -= 20
    player.casa["comida"]['Arroz'] += 1
    s('clear')
    print('Você comprou um Pote de Arroz com sucesso')
    sleep(2)
    s('clear')
    lojaitens()
  elif iten == '6' and player.coins['moedacobre'] >= 20:
    player.coins['moedacobre'] -= 20
    player.casa["comida"]['Bife'] += 1
    s('clear')
    print('Você comprou um Bife com sucesso')
    sleep(2)
    s('clear')
    lojaitens()
  elif iten == '7' and player.coins['moedacobre'] >= 20:
    player.coins['moedacobre'] -= 20
    player.casa["comida"]['Frango'] += 1
    s('clear')
    print('Você comprou um Frango com sucesso')
    sleep(2)
    s('clear')
    lojaitens()
  elif iten == '8' and player.coins['moedacobre'] >= 50:
    player.coins['moedacobre'] -= 50
    sla = 1
    while True:
      try:
        if player.itens['itens']['iten' + str(sla)]['nome'] == 'Perfume Anti-Monstro':
          player.itens['itens']['iten' + str(sla)]['quantia'] += 1
          break
        else:
          sla += 1
      except:
        player.itens['itens']['iten' + str(sla)] = {
          'nome': 'Perfume Anti-Monstro',
          'bufftipo': 'Anti Monstro',
          'buff': 4,
          'desc': 'Diminui a chance de ser atacado',
          'quantia': 1
        }
        break
    s('clear')
    print('Você comprou um Perfume Anti-Monstro com sucesso')
    sleep(2)
    s('clear')
    lojaitens()
  elif iten == '9' and player.coins['moedacobre'] >= 50:
    player.coins['moedacobre'] -= 50
    sla = 1
    while True:
      try:
        if player.itens['itens']['iten' + str(sla)]['nome'] == 'Perfume Monstro':
          player.itens['itens']['iten' + str(sla)]['quantia'] += 1
          break
        else:
          sla += 1
      except:
        player.itens['itens']['iten' + str(sla)] = {
          'nome': 'Perfume Monstro',
          'bufftipo': 'Monstro',
          'buff': 2,
          'desc': 'Aumenta a chance de ser atacado por um monstro',
          'quantia': 1
        }
        break
    s('clear')
    print('Você comprou um Perfume Monstro com sucesso')
    sleep(2)
    s('clear')
    lojaitens()
  elif iten == '10' and player.coins['moedacobre'] >= 150:
    player.coins['moedacobre'] -= 150
    sla = 1
    while True:
      try:
        if player.itens['itens']['iten' + str(sla)]['nome'] == 'Drop Buffer':
          player.itens['itens']['iten' + str(sla)]['quantia'] += 1
          break
        else:
          sla += 1
      except:
        player.itens['itens']['iten' + str(sla)] = {
          'nome': 'Drop Buffer',
          'bufftipo': 'Drop',
          'buff': 20,
          'desc':
          'Aumenta os drops comuns do monstro e aumenta a chance de dropar algum item',
          'quantia': 1
        }
        break
    s('clear')
    print('Você comprou um Drop Buffer com sucesso')
    sleep(2)
    s('clear')
    lojaitens()

  else:
    s('clear')
    print('Você não tem moedas o suficiente ou insiriu algo invalido')
    sleep(2)
    s('clear')
    lojaitens()


def lojaquipamentos():
  global player
  if player.classe == 'Mago':
    equipamento = input('''
        Loja de Equipamentos
(1) Voltar

        (2)
Cajado de Madeira Velha
90 Moedas de Cobre
20% de Buff de Ataque


              -->''')
    if equipamento == '2' and player.coins['moedacobre'] >= 70:
      player.coins['moedacobre'] -= 70
      sla = 1
      while True:
        try:
          if player.equipamento['equipamento' + str(sla)] not in player.equipamento:
            pass
          sla += 1
        except:
          player.equipamento['equipamento' + str(sla)] = {
            'nome': 'Cajado de Madeira Velha',
            'buff': 20
          }
          break
      print(
        'Cajado de Madeira Velha comprada com sucesso, equipe-a em <Personagem> '
      )
      sleep(3)
      s('clear')
    elif equipamento == '1':
      s('clear')
      loja()
    else:
      s('clear')
      print('Você não tem dinheiro o suficiente ou insiriu algo invalido')
      sleep(2)
      s('clear')
      lojaquipamentos()
  elif player.classe == 'Cavaleiro':
    equipamento = input('''
        Loja de Equipamentos
(1) Voltar

        (2)
Espada de Cobre
70 Moedas de Cobre
20% de Buff de Ataque


              -->''')
    if equipamento == '2' and player.coins['moedacobre'] >= 70:
      player.coins['moedacobre'] -= 70
      sla = 1
      while True:
        try:
          if player.equipamento['equipamento' + str(sla)] not in player.equipamento:
            pass
          sla += 1
        except:
          player.equipamento['equipamento' + str(sla)] = {
            'nome': 'Espada de Ferro',
            'buff': 20
          }
          break

      print('Espada de Ferro comprada com sucesso, equipe-a em <Personagem> ')
      sleep(3)
      s('clear')
    elif equipamento == '1':
      s('clear')
      loja()
    else:
      s('clear')
      print('Você não tem dinheiro o suficiente ou insiriu algo invalido')
      sleep(2)
      s('clear')
      lojaquipamentos()
  elif player.classe == 'Arqueiro':
    equipamento = input('''
        Loja de Equipamentos
(1) Voltar

        (2)
Arco de Madeira
70 Moedas de Cobre
25% de Buff de Ataque


              -->''')
    if equipamento == '2' and player.coins['moedacobre'] >= 70:
      player.coins['moedacobre'] -= 70
      sla = 1
      while True:
        try:
          if player.equipamento['equipamento' + str(sla)] not in player.equipamento:
            pass
          sla += 1
        except:
          player.equipamento['equipamento' + str(sla)] = {
            'nome': 'Arco de Madeira',
            'buff': 25
          }
          break

      print('Arco de Madeira comprada com sucesso, equipe-a em Personagem ')
      sleep(3)
      s('clear')
    elif equipamento == '1':
      s('clear')
      loja()
    else:
      s('clear')
      print('Você não tem dinheiro o suficiente ou insiriu algo invalido')
      sleep(2)
      s('clear')
      lojaquipamentos()


def lojapoçoes():
  global player
  poçao = input('''
        Loja de Poções

(1) Voltar
(2) Poção de Esquiva [80 Moedas de Cobre]
(3) Poção de Poder [50 Moedas de Cobre]
(4) Poção de Mana [30 Moedas de Cobre]
(5) Poção de Vida [30 Moedas de Cobre]


          -->''')
  if poçao == '2' and player.coins['moedacobre'] >= 80:
    player.coins['moedacobre'] -= 80
    player.poçao['Esquiva'] += 1
    print('Você comprou uma poção de esquiva com sucesso')
    sleep(2)
    s('clear')
    lojapoçoes()
  elif poçao == '3' and player.coins['moedacobre'] >= 50:
    player.coins['moedacobre'] -= 50
    player.poçao['Poder'] += 1
    print('Você comprou uma poção de poder com sucesso')
    sleep(2)
    s('clear')
    lojapoçoes()
  elif poçao == '4' and player.coins['moedacobre'] >= 30:
    player.coins['moedacobre'] -= 30
    player.poçao['Mana'] += 1
    print('Você comprou uma poção de mana com sucesso')
    sleep(2)
    s('clear')
    lojapoçoes()
  elif poçao == '5' and player.coins['moedacobre'] >= 30:
    player.coins['moedacobre'] -= 30
    player.poçao['Vida'] += 1
    print('Você comprou uma poção de vida com sucesso')
    sleep(2)
    s('clear')
    lojapoçoes()
  elif poçao == '1':
    s('clear')
    loja()
  else:
    s('clear')
    print('Você não tem moedas o suficiente ou insiriu algo invalido')
    sleep(1.5)
    s('clear')
    lojapoçoes()

def lojaarmadura():
  global player
  armadura = input('''
      Loja de Armaduras

(1) Voltar

      (2)                 |      (3)                                                                                                          
Armadura de Couro         | Armadura de Cobre                                                                                                        
100 Moedas de Cobre       | 200 Moedas de Cobre                                                                                                          
Buffs: 10% a mais de vida | Buffs: 15% a mais de vida
                          | 5% a mais de mana                                                                                       
  
  
                  -->''')
  if armadura == '1':
    s('clear')
    loja()
  elif armadura == '2' and player.coins['moedacobre'] >= 100:
    player.coins['moedacobre'] -= 100
    armadu = 1
    while True:
      try:
        if player.armadura['armadura' + str(armadu)]['nome'] == 'teste':
          pass
        armadu += 1
      except:
        player.armadura['armadura' + str(armadu)] = {'nome': 'Armadura de Couro', 'desc': '10% a mais de vida', 'bufftipo1': 'Vida', 'buff1': 10}
        break
    s('clear')
    print('Você comprou uma Armadura de Couro equipe-a em <Personagem>')
    sleep(4)
    s('clear')
    lojaarmadura()
  elif armadura == '3' and player.coins['moedacobre'] >= 200:
    player.coins['moedacobre'] -= 200
    armadu = 1
    while True:
      try:
        if player.armadura['armadura' + str(armadu)]['nome'] == 'teste':
          pass
        armadu += 1
      except:
        player.armadura['armadura' + str(armadu)] = {'nome': 'Armadura de Cobre', 'desc': '15% a mais de vida e 5% a mais de mana', 'bufftipo1': 'Vida', 'bufftipo2': 'Mana', 'buff1': 15, 'buff2': 5}
        break
    s('clear')
    print('Você comprou uma Armadura de Cobre equipe-a em <Personagem>')
    sleep(4)
    s('clear')
    lojaarmadura()
  else:
    s('clear')
    print('Você não tem moedas o suficiente ou insiriu algo invalido')
    sleep(1.5)
    s('clear')
    lojaarmadura()

def loja():
  global player
  loja = input('''
          Loja
(1) Itens/Acessorios/Comidas
(2) Poções
(3) Equipamentos
(4) Armaduras
(5) Voltar

        -->''')

  if loja == '1':
    s('clear')
    lojaitens()
  elif loja == '2':
    s('clear')
    lojapoçoes()
  elif loja == '3':
    s('clear')
    lojaquipamentos()
  elif loja == '4':
    s('clear')
    lojaarmadura()
  elif loja == '5':
    s('clear')
    lugarsalvo()
  else:
    s('clear')
    print(inva)
    s('clear')
    sleep(1.5)
    loja()


def mestrehabusken():
  global player
  if player.bossderrotado['Slime Gigante'] == 'sim':
    mestre = input(f'''
      Mestre de Habusken

(1) Treinar [50 moedas de cobre]
{player.treinamento['habusken']}% do Treino Concluido
(2) Voltar


        -->''')
    if mestre == '1':
      if player.coins['moedacobre'] >= 50:
        sla = 0
        player.coins['moedacobre'] -= 50
        letras = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                  'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                  'Y', 'Z')

        letra1 = choice(letras)
        letra2 = choice(letras)
        letra3 = choice(letras)
        letra4 = choice(letras)
        letra5 = choice(letras)
        letra6 = choice(letras)
        letra7 = choice(letras)
        letra8 = choice(letras)
        letra9 = choice(letras)
        letra10 = choice(letras)
        letra = [
          letra1, letra2, letra3, letra4, letra5, letra6, letra7, letra8,
          letra9, letra10
        ]

        print(
          'Aparecera letras aleatorias na tela, voce tera 3 segundos para digitar apenas a letra que está aparecendo, não dê enter e nem digite outras letras, se acertar todas as letras você completa 10% do treino'
        )
        sleep(5)
        print('começando em 5')
        sleep(1)
        print('4')
        sleep(1)
        print('3')
        sleep(1)
        print('2')
        sleep(1)
        print('1')
        sleep(1)
        s('clear')
        while True:
          if sla == 10:
            break
          else:
            sla += 1
            top = '''
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                
                                                                                                '''
            top2 = -len(top)
            top = list(top)
            top[randint(top2, -1)] = letra[sla - 1]
            top = ' '.join(top)
            print(top)
            sleep(3)
            s('clear')

        treinar = input(cores.green + 'Enter para continuar' + cores.negrito)
        treinar = treinar.split()
        treino = 0
        if letra10 == treinar[-1].upper():
          treino += 1
        if letra9 == treinar[-2].upper():
          treino += 1
        if letra8 == treinar[-3].upper():
          treino += 1
        if letra7 == treinar[-4].upper():
          treino += 1
        if letra6 == treinar[-5].upper():
          treino += 1
        if letra5 == treinar[-6].upper():
          treino += 1
        if letra4 == treinar[-7].upper():
          treino += 1
        if letra3 == treinar[-8].upper():
          treino += 1
        if letra2 == treinar[-9].upper():
          treino += 1
        if letra1 == treinar[-10].upper():
          treino += 1
        player.treinamento['habusken'] += treino
        print(
          f'Você acertou um total de {treino} letras, aumentando a taxa de conclusão do treino em {treino}%'
        )
        sleep(3)
        if player.treinamento['habusken'] >= 100:
          if player.treinamento['habusken'] > 100:
            player.treinamento['habusken'] = 100
          print(
            'Você concluiu o treinamento!! Você aprendeu Etén, que é uma variante da Mana só que mais poderosa, agora em todos os seus ataques terão um buff de 30% a mais de dano'
          )
          player.eten = 'sim'

      else:
        s('clear')
        print('Você não tem 50 moedas de cobre')
        sleep(2)
        s('clear')
        mestrehabusken()
    elif mestre == '2':
      s('clear')
      vilahabusken()
    else:
      s('clear')
      print(inva)
      sleep(1.5)
      s('clear')
      mestrehabusken()
  else:
    s('clear')
    print(
      'O Mestre de Habusken não te reconhece como discipulo, mate o boss do primeiro andar para provar seu valor ao mestre'
    )
    sleep(2.5)
    s('clear')
    vilahabusken()


explo = 0


def exploprint(andar):
  global explo
  out = ""
  for y in explo:
    for x in y:
      out += x
    out += "\n"
  print(f'                Andar {andar}\n ')
  print(out)
  print('\n "E" para voltar\nWASD para mover ou as setinhas para se mover\n')


def find_loc():
  global explo
  for y in range(len(explo)):
    for x in range(len(explo[y])):
      if explo[y][x] == "& ":
        return y, x


def explorar(dungeon, andar):
  global player, explo, monstroatual, monstroandar1habusken, monstrohabusken
  if dungeon == 'habusken':
    if andar == 1:

      explo = [[
        "**", "**", "**", "**", "**", "**", "**", "| ", "6 ", "|*", "**", "**",
        "/ ", "3 ", "+ ", "/ ", "******", "**"
      ],
               [
                 "**", "**", "**", "**", "**", "**", "**", "| ", "+ ", "|*",
                 "**", "*", "/ ", "+ ", "+ ", "/ ", "**", "*******"
               ],
               [
                 "**", "**", "**", "**", "**", "**", "**", "| ", "+ ", "|*",
                 "*", "*/ ", "+ ", "+ ", "/ ", "**", "**", "******"
               ],
               [
                 "**", "**", "**", "**", "**", "**", "**", "| ", "+ ", "|*",
                 "*/", "+ ", "+ ", " / ", "**", "**", "**", "*****"
               ],
               [
                 "**", "**", "**", "**", "**", "**", "**", "| ", "+ ", "|",
                 "*/ ", "+ ", "  / ", "--", "--", "--", "--", "----"
               ],
               [
                 "**", "**", "**", "**", "**", "**", " ", "/ ", "+ ", "+ ",
                 "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ",
                 "4 "
               ],
               [
                 "----", "", "--", "--", "--", "--", "/ ", "+ ", "+ ", "& ",
                 "+ ", "+ ", " /", "--", "--", "----------"
               ],
               [
                 "1 ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ",
                 "+ ", "+ ", "|**", "**", "**", "**", "*****", "**"
               ],
               [
                 "--", "--", "--", "--", "--", "--", "--", "| ", "+ ", "|**",
                 "\ ", "+ ", "\**", "**", "**", "**", "****", "**"
               ],
               [
                 "****", "**", "**", "**", "**", "**", "", "| ", "+ ", "|***",
                 "\ ", "+ ", "\*", "***", "**", "**", "***", "**"
               ],
               [
                 "****", "**", "**", "**", "**", "**", "", "| ", "+ ", "|*",
                 "***\ ", "+ ", "\*", "**", "***", "**", "**", "**"
               ],
               [
                 "****", "**", "**", "**", "**", "*", "", "/ ", "+ ", "/*",
                 "*****\ ", "+ ", "\*", "**", "***", "***", "**"
               ],
               [
                 "****", "**", "**", "**", "**", "", "", "/ ", "+ ", "/*",
                 "*******\ ", "+ ", "\*", "**", "**", "*", "**", "**"
               ],
               [
                 "****", "**", "**", "**", "*", "", "", "/ ", "+ ", "/*",
                 "*********\ ", "+ ", "\*", "***", "", "**", "*", "**"
               ],
               [
                 "****", "**", "**", "*", "*", "", "", "| ", "2 ", "|*",
                 "***********\ ", "5 ", "\*", "***", "*", "*", "*", "*"
               ]]
      exploprint(1)
      print('\n')
      while True:
        loc = find_loc()
        key = getkey()
        if key == keys.LEFT or key == keys.A:
          try:
            if explo[loc[0]][loc[1] - 1] == '1 ':
              print('Você foi para o Caminho 1')
              sleep(3)
              break
            elif explo[loc[0]][loc[1] - 1] == '3 ':
              print('Você foi para o Caminho 3')
              sleep(3)
              break
            else:
              if explo[loc[0]][loc[1] - 1] == '+ ':
                explo[loc[0]][loc[1] - 1] = "& "
                explo[loc[0]][loc[1]] = "+ "
              s('clear')
              exploprint(1)
          except:
            pass
        elif key == keys.RIGHT or key == keys.D:
          try:
            if explo[loc[0]][loc[1] + 1] == '4 ':
              print('Você foi para o Caminho 4')
              sleep(3)
              break
            else:
              if explo[loc[0]][loc[1] + 1] == '+ ':
                explo[loc[0]][loc[1] + 1] = "& "
                explo[loc[0]][loc[1]] = "+ "
              s('clear')
              exploprint(1)
          except:
            pass
        elif key == keys.UP or key == keys.W:
          try:
            if explo[loc[0] - 1][loc[1]] == '6 ':
              print('Você foi para o Caminho 6')
              sleep(3)
              break
            else:
              if explo[loc[0] - 1][loc[1]] == '+ ':
                explo[loc[0] - 1][loc[1]] = "& "
                explo[loc[0]][loc[1]] = "+ "
              s('clear')
              exploprint(1)
          except:
            pass
        elif key == keys.DOWN or key == keys.S:
          try:
            if explo[loc[0] + 1][loc[1]] == '2 ':
              print('Você foi para o Caminho 2')
              sleep(3)
              break
            elif explo[loc[0] + 1][loc[1]] == '5 ':
              print('Você foi para o Caminho 5')
              sleep(3)
              break
            else:
              if explo[loc[0] + 1][loc[1]] == '+ ':
                explo[loc[0] + 1][loc[1]] = "& "
                explo[loc[0]][loc[1]] = "+ "
              s('clear')
              exploprint(1)
          except:
            pass
        elif key == keys.E:
          s('clear')
          dungeonhabusken()
          break
      ab = randint(2, 3)
      f = 1
      while True:
        try:
          if player.itenusado['Efeito']['bufftipo' + str(f)] == 'Monstro':
            print(
              'Devido ao item usado a chance de ser atacado foi aumentada, o efeito se passou'
            )
            sleep(3)
            s('clear')
            ab = randint(1, player.itenusado['Efeito']['buff' + str(f)])
            del player.itenusado['Efeito']['bufftipo' + str(f)]
            del player.itenusado['Efeito']['buff' + str(f)]
            break
          else:
            f += 1
        except:
          break
      try:
        if player.equipado['acessorio']['bufftipo'] == 'Boss':
          print(
            'Chance de achar a sala do boss aumentada devido ao acessorio usado'
          )
          sleep(3)
          s('clear')
          chance = player.equipado['acessorio']['buff']
        else:
          chance = 8
      except:
        chance = 8

      if randint(1, chance) == 3:
        print('Você encontrou a sala do boss!')
        while True:
          sin = input('Deseja entrar para batalhar com o boss? Sim/Nao -->')
          if unidecode(sin.upper()) == 'SIM' or unidecode(sin.upper()) == 'S':
            s('clear')
            player.umavez = 1
            monstroatual = Monstros().Habusken().Andar1Habusken().SlimeGigante
            batalhar(monstroatual)
            aaa = False
            break
          elif unidecode(sin.upper()) == 'NAO' or unidecode(
              sin.upper()) == 'N':
            s('clear')
            lugarsalvo()
            aaa = False
            break
          else:
            s('clear')
            print(inva)
            sleep(1.5)
            s('clear')

      elif ab == 2:
        top = ('Slime', 'Slime', 'Slime', 'Kobold', 'Kobold', 'Lobo')
        a = choice(top)
        while True:
          sla2 = input(
            f'Você encontrou um {a}, deseja lutar com ele? Sim/Nao -->')
          if unidecode(sla2.upper()) == 'SIM' or unidecode(
              sla2.upper()) == 'S':
            s('clear')
            player.umavez = 1
            if a == 'Slime':
              monstroatual = Monstros().Habusken().Andar1Habusken().Slime
              batalhar(monstroatual)
            elif a == 'Kobold':
              monstroatual = Monstros().Habusken().Andar1Habusken().Kobold
              batalhar(monstroatual)
            elif a == 'Lobo':
              monstroatual = Monstros().Habusken().Andar1Habusken().Lobo
              batalhar(monstroatual)
            aaa = False
            break
          elif unidecode(sla2.upper()) == 'NAO' or unidecode(
              sla2.upper()) == 'N':
            s('clear')
            lugarsalvo()
            aaa = False
            break
          else:
            s('clear')
            print(inva)
            sleep(1.5)
            s('clear')
      else:
        abc = randint(1, 3)
        if abc == 1 or abc == 3:
          moeda = randint(5, 15)
          player.coins['moedacobre'] += moeda
          print(f'Você encontrou {moeda} moedas de cobre!!')
        else:
          print('Você explorou a dungeon e não encontrou nada')

        sleep(1.5)
        s('clear')
        lugarsalvo()
    elif andar == 2:
      explo = [[
        "**", "**", "**", "**", "**", "**", "**", "| ", "6 ", "|*", "**", "**",
        "/ ", "3 ", "+ ", "/ ", "******", "**"
      ],
               [
                 "**", "**", "**", "**", "**", "**", "**", "| ", "+ ", "|*",
                 "**", "*", "/ ", "+ ", "+ ", "/ ", "**", "*******"
               ],
               [
                 "**", "**", "**", "**", "**", "**", "**", "| ", "+ ", "|*",
                 "*", "*/ ", "+ ", "+ ", "/ ", "**", "**", "******"
               ],
               [
                 "**", "**", "**", "**", "**", "**", "**", "| ", "+ ", "|*",
                 "*/", "+ ", "+ ", " / ", "**", "**", "**", "*****"
               ],
               [
                 "**", "**", "**", "**", "**", "**", "**", "| ", "+ ", "|",
                 "*/ ", "+ ", "  / ", "--", "--", "--", "--", "----"
               ],
               [
                 "**", "**", "**", "**", "**", "**", " ", "/ ", "+ ", "+ ",
                 "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ",
                 "4 "
               ],
               [
                 "----", "", "--", "--", "--", "--", "/ ", "+ ", "+ ", "& ",
                 "+ ", "+ ", " /", "--", "--", "----------"
               ],
               [
                 "1 ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ", "+ ",
                 "+ ", "+ ", "|**", "**", "**", "**", "*****", "**"
               ],
               [
                 "--", "--", "--", "--", "--", "--", "--", "| ", "+ ", "|**",
                 "\ ", "+ ", "\**", "**", "**", "**", "****", "**"
               ],
               [
                 "****", "**", "**", "**", "**", "**", "", "| ", "+ ", "|***",
                 "\ ", "+ ", "\*", "***", "**", "**", "***", "**"
               ],
               [
                 "****", "**", "**", "**", "**", "**", "", "| ", "+ ", "|*",
                 "***\ ", "+ ", "\*", "**", "***", "**", "**", "**"
               ],
               [
                 "****", "**", "**", "**", "**", "*", "", "/ ", "+ ", "/*",
                 "*****\ ", "+ ", "\*", "**", "***", "***", "**"
               ],
               [
                 "****", "**", "**", "**", "**", "", "", "/ ", "+ ", "/*",
                 "*******\ ", "+ ", "\*", "**", "**", "*", "**", "**"
               ],
               [
                 "****", "**", "**", "**", "*", "", "", "/ ", "+ ", "/*",
                 "*********\ ", "+ ", "\*", "***", "", "**", "*", "**"
               ],
               [
                 "****", "**", "**", "*", "*", "", "", "| ", "2 ", "|*",
                 "***********\ ", "5 ", "\*", "***", "*", "*", "*", "*"
               ]]
      exploprint(2)
      print('\n')
      while True:
        key = getkey()
        loc = find_loc()
        if key == keys.LEFT or key == keys.A:
          try:
            if explo[loc[0]][loc[1] - 1] == '1 ':
              print('Você foi para o Caminho 1')
              sleep(3)
              break
            elif explo[loc[0]][loc[1] - 1] == '3 ':
              print('Você foi para o Caminho 3')
              sleep(3)
              break
            else:
              if explo[loc[0]][loc[1] - 1] == '+ ':
                explo[loc[0]][loc[1] - 1] = "& "
                explo[loc[0]][loc[1]] = "+ "
              s('clear')
              exploprint(2)
          except:
            pass
        elif key == keys.RIGHT or key == keys.D:
          try:
            if explo[loc[0]][loc[1] + 1] == '4 ':
              print('Você foi para o Caminho 4')
              sleep(3)
              break
            else:
              if explo[loc[0]][loc[1] + 1] == '+ ':
                explo[loc[0]][loc[1] + 1] = "& "
                explo[loc[0]][loc[1]] = "+ "
              s('clear')
              exploprint(2)
          except:
            pass
        elif key == keys.UP or key == keys.W:
          try:
            if explo[loc[0] - 1][loc[1]] == '6 ':
              print('Você foi para o Caminho 6')
              sleep(3)
              break
            else:
              if explo[loc[0] - 1][loc[1]] == '+ ':
                explo[loc[0] - 1][loc[1]] = "& "
                explo[loc[0]][loc[1]] = "+ "
              s('clear')
              exploprint(2)
          except:
            pass
        elif key == keys.DOWN or key == keys.S:
          try:
            if explo[loc[0] + 1][loc[1]] == '2 ':
              print('Você foi para o Caminho 2')
              sleep(3)
              break
            elif explo[loc[0] + 1][loc[1]] == '5 ':
              print('Você foi para o Caminho 5')
              sleep(3)
              break
            else:
              if explo[loc[0] + 1][loc[1]] == '+ ':
                explo[loc[0] + 1][loc[1]] = "& "
                explo[loc[0]][loc[1]] = "+ "
              s('clear')
              exploprint(2)
          except:
            pass
        elif key == keys.E:
          s('clear')
          dungeonhabusken()
          break
      ab = randint(1, 3)
      f = 1
      while True:
        try:
          if player.itenusado['Efeito']['bufftipo' + str(f)] == 'Monstro':
            print(
              'Devido ao item usado a chance de ser atacado foi aumentada, o efeito se passou'
            )
            sleep(3)
            s('clear')
            ab = randint(1, player.itenusado['Efeito']['buff' + str(f)])
            del player.itenusado['Efeito']['bufftipo' + str(f)]
            del player.itenusado['Efeito']['buff' + str(f)]
            break
          else:
            f += 1
        except:
          break
      try:
        if player.equipado['acessorio']['bufftipo'] == 'Boss':
          print(
            'Chance de achar a sala do boss aumentada devido ao acessorio usado'
          )
          sleep(3)
          s('clear')
          chance = player.equipado['acessorio']['buff']
        else:
          chance = 8
      except:
        chance = 8
      if randint(1, chance) == 3:
        print('Você encontrou a sala do boss!')
        while True:
          sin = input('Deseja entrar para batalhar com o boss? Sim/Nao -->')
          if unidecode(sin.upper()) == 'SIM' or unidecode(sin.upper()) == 'S':
            s('clear')
            player.umavez = 1
            monstroatual = Monstros().Habusken().Andar2Habusken().GoblinXama
            batalhar(monstroatual)

          elif unidecode(sin.upper()) == 'NAO' or unidecode(
              sin.upper()) == 'N':
            s('clear')
            lugarsalvo()

          else:
            s('clear')
            print(inva)
            sleep(1.5)
            s('clear')

      elif ab == 1:
        top = ('Goblin', 'Goblin', 'Goblin', 'Esqueleto', 'Kobold Mago',
               'Esqueleto')
        a = choice(top)
        while True:
          sla2 = input(
            f'Você encontrou um {a}, deseja lutar com ele? Sim/Nao -->')
          if unidecode(sla2.upper()) == 'SIM' or unidecode(
              sla2.upper()) == 'S':
            s('clear')
            player.umavez = 1
            if a == 'Esqueleto':
              monstroatual = Monstros().Habusken().Andar2Habusken().Esqueleto
              batalhar(monstroatual)
            elif a == 'Kobold Mago':
              monstroatual = Monstros().Habusken().Andar2Habusken().KoboldMago
              batalhar(monstroatual)
            elif a == 'Goblin':
              monstroatual = Monstros().Habusken().Andar2Habusken().Goblin
              batalhar(monstroatual)
          elif unidecode(sla2.upper()) == 'NAO' or unidecode(
              sla2.upper()) == 'N':
            s('clear')
            lugarsalvo()

          else:
            s('clear')
            print(inva)
            sleep(1.5)
            s('clear')
      else:
        abc = randint(1, 3)
        if abc == 1 or abc == 3:
          moeda = randint(5, 15)
          player.coins['moedacobre'] += moeda
          print(f'Você encontrou {moeda} moedas de cobre!!')
        else:
          print('Você explorou a dungeon e não encontrou nada')
        sleep(1.5)
        s('clear')
        lugarsalvo()


def anima(animacao):
  if animacao == 'andar':
    s('clear')
    print('Andando pelo caminho.')
    sleep(0.5)
    s('clear')
    print('Andando pelo caminho..')
    sleep(0.5)
    s('clear')
    print('Andando pelo caminho...')
    sleep(0.5)
    s('clear')
    print('Andando pelo caminho.')
    sleep(0.5)
    s('clear')
    print('Andando pelo caminho..')
    sleep(0.5)
    s('clear')
    print('Andando pelo caminho...')
    sleep(0.5)
  if animacao == 'subir':
    s('clear')
    print('Subindo de Andar.')
    sleep(0.5)
    s('clear')
    print('Subindo de Andar..')
    sleep(0.5)
    s('clear')
    print('Subindo de Andar...')
    sleep(0.5)
    s('clear')
    print('Subindo de Andar.')
    sleep(0.5)
    s('clear')
    print('Subindo de Andar..')
    sleep(0.5)
    s('clear')
    print('Subindo de Andar...')
    sleep(0.5)
  if animacao == 'descer':
    s('clear')
    print('Descendo de Andar.')
    sleep(0.5)
    s('clear')
    print('Descendo de Andar..')
    sleep(0.5)
    s('clear')
    print('Descendo de Andar...')
    sleep(0.5)
    s('clear')
    print('Descendo de Andar.')
    sleep(0.5)
    s('clear')
    print('Descendo de Andar..')
    sleep(0.5)
    s('clear')
    print('Descendo de Andar...')
    sleep(0.5)




antelugar = ''


def dungeonhabusken():
  global player, andar, antelugar
  player.lugar = 'habusken'
  antelugar = 'habusken'
  if andar == 1:
    if player.umavez == 1:
      print('''
Você se encontra no andar 1 da dungeon, a dungeon de habusken vai até o andar 5, para subir de andar você deve encontrar
a sala do Boss em cada andar. após derrota-lo você pode subir o andar quando você quiser, para encontrar a sala do boss você
deve explorar a dungeon, ela é bem dificil de se encontrar.''')
      player.umavez = 0
      input(cores.green + 'Enter para continuar' + cores.negrito)
    s('clear')
    print('''
            Andar 1 da Dungeon de Habusken
           Recomendado para iniciantes de nivel 1 a 5

    O que deseja fazer?
(1) Explorar
(2) Itens
(3) Sair da Dungeon''')
    if player.bossderrotado['Slime Gigante'] == 'sim':
      print('(4) Subir de Andar')
    esco1 = input('''
      -->''')
    if esco1 == '1':
      s('clear')
      explorar('habusken', 1)
    elif esco1 == '2':
      s('clear')
      inventario()
    elif esco1 == '3':
      s('clear')
      vilahabusken()
    elif esco1 == '4' and player.bossderrotado['Slime Gigante'] == 'sim':
      andar = 2
      player.umavez = 1
      s('clear')
      anima('subir')
      s('clear')
      dungeonhabusken()
    else:
      print(inva)
      sleep(1.5)
      s('clear')
      dungeonhabusken()
  elif andar == 2:
    if player.umavez == 1:
      player.umavez = 0
      print('Você subiu para o segundo andar')
      print('''
Os monstros presentes nesse andar são:
Goblin: nivel 5
Kobold Mago: nivel 8
Esqueleto: nivel 10
        BOSS
Goblin Xamã: nivel 15''')
      input(cores.green + 'Enter para continuar' + cores.negrito)
    s('clear')
    print('''
            Andar 2 da Dungeon de Habusken
         Recomendado para jogadores de nivel 5 a 10

    O que deseja fazer?
(1) Explorar
(2) Itens
(3) Descer de Andar''')
    if player.bossderrotado['Goblin Xama'] == 'sim':
      print('(4) Subir de Andar')
    esco1 = input('''
      -->''')
    if esco1 == '1':
      s('clear')
      explorar('habusken', 2)
    elif esco1 == '2':
      s('clear')
      inventario()
    elif esco1 == '3':
      s('clear')
      andar = 1
      anima('descer')
      s('clear')
      dungeonhabusken()
    elif esco1 == '4' and player.bossderrotado['Goblin Xama'] == 'sim':
      andar = 3
      player.umavez = 1
      s('clear')
      anima('subir')
      s('clear')
      dungeonhabusken()
    else:
      print(inva)
      sleep(1.5)
      s('clear')
      dungeonhabusken()


def curandeira():
  global player
  while True:
    cura = input(cores.pink + '''
            Curandeira
(1) Restaurar Vida [1 moedas de cobre para cada 5 de vida]
(2) Restaurar Mana [1 moedas de cobre para cada 5 de mana]
(3) Voltar

    -->''' + cores.negrito)
    if cura == '1':
        val = input('Quanto de vida deseja restaurar? -->')
        val = sub(' ', '', val)
        certo = val.isnumeric()
        if certo == False:
          s('clear')
          print('Insira apenas numeros')
          sleep(2)
          s('clear')
          curandeira()
        else:
          val = int(val)          
          gasto = trunc(val / 5)
          if val > player.vida['vidamax'] - player.vida['vida']:
            print(
              f'É necesario {player.vida["vidamax"] - player.vida["vida"]} para recuperar totalmente sua vida, o valor que você insiriu é maior que isso'
            )
            input(cores.green + 'Enter para continuar' + cores.negrito)
          gastar = input(
            f'Isto irá custar {gasto} moedas de cobre, tem certeza? Sim/Nao -->'
          )
          if unidecode(gastar.upper()) == 'SIM' or unidecode(
              gastar.upper()) == 'S':
            if player.coins['moedacobre'] >= gasto:
              player.coins['moedacobre'] -= gasto
              player.vida['vida'] += val
              if player.vida['vida'] > player.vida['vidamax']:
                player.vida['vida'] = player.vida['vidamax']
              print('Vida restaurada com sucesso')
              sleep(1.5)
              s('clear')
              curandeira()
            else:
              print(cores.yellow +
                    'Você não tem moedas de cobre o suficiente' +
                    cores.negrito)
              sleep(1.5)
              s('clear')
              curandeira()
              
          elif unidecode(gastar.upper()) == 'NAO' or unidecode(
              gastar.upper()) == 'N':
            s('clear')
            curandeira()
            
          else:
            s('clear')
            print(inva)
            sleep(1.5)
            curandeira()
            
    elif cura == '2':
        val = input('Quanto de mana deseja restaurar? -->')
        val = sub(' ', '', val)
        certo = val.isnumeric()
        if certo == False:
          s('clear')
          print('Insira apenas numeros')
          sleep(2)
          s('clear')
          curandeira()
        else:
          val = int(val)
          gasto = trunc(val / 5)
          if val > player.mana['manamax'] - player.mana['mana']:
            print(
              f'É necesario {player.mana["manamax"] - player.mana["mana"]} para recuperar totalmente sua mana, o valor que você insiriu é maior que isso'
            )
            input(cores.green + 'Enter para continuar' + cores.negrito)
          gastar = input(
            f'Isto irá custar {gasto} moedas de cobre, tem certeza? Sim/Nao -->'
          )
          if unidecode(gastar.upper()) == 'SIM' or unidecode(
              gastar.upper()) == 'S':
            if player.coins['moedacobre'] >= gasto:
              player.coins['moedacobre'] -= gasto
              player.mana['mana'] += val
              if player.mana['mana'] > player.mana['manamax']:
                player.mana['mana'] = player.mana['manamax']
              print('Mana restaurada com sucesso')
              sleep(1.5)
              s('clear')
              curandeira()
            else:
              print(cores.yellow +
                    'Você não tem moedas de cobre o suficiente' +
                    cores.negrito)
              sleep(1.5)
              s('clear')
              curandeira()
              
          elif unidecode(gastar.upper()) == 'NAO' or unidecode(
              gastar.upper()) == 'N':
            s('clear')
            curandeira()
            
          else:
            s('clear')
            print(inva)
            sleep(1.5)
            curandeira()
            
        

    elif cura == '3':
      s('clear')
      lugarsalvo()
    else:
      print(inva)
      sleep(1.5)
      s('clear')


def skillequip():
  global player
  print('''
        Habilidades Atuais

(1) Voltar\n''')
  print(f'''
Habilidade 1: 
{player.hab1['nome']}
Mana: {player.hab1['mana']}
Dano Base: {player.hab1['dano']}
''')
  try:
    print(f'Quantia: {player.hab1["quantia"]}')
  except:
    pass
  try:
    print(f'Efeito: {player.hab1["efeito"]}')
  except:
    pass
  print(f'''
Habilidade 2: 
{player.hab2['nome']}
Mana: {player.hab2['mana']}
Dano Base: {player.hab2['dano']}
''')
  try:
    print(f'Quantia: {player.hab2["quantia"]}')
  except:
    pass
  try:
    print(f'Efeito: {player.hab2["efeito"]}')
  except:
    pass
  print(f'''
Habilidade 3: 
{player.hab3['nome']}
Mana: {player.hab3['mana']}
Dano Base: {player.hab3['dano']}
''')
  try:
    print(f'Quantia: {player.hab3["quantia"]}')
  except:
    pass
  try:
    print(f'Efeito: {player.hab3["efeito"]}')
  except:
    pass
  print('''
        Habilidades Equipaveis\n''')
  habilidades = 1
  habilidade1 = 1
  while True:
    try:
      habilidades += 1
      print(
        f'\n         ({habilidades})\nNome: {player.habs["habilidade" + str(habilidade1)]["nome"]}\nMana: {player.habs["habilidade" + str(habilidade1)]["mana"]}\nDano Base: {player.habs["habilidade" + str(habilidade1)]["dano"]}'
      )
      try:
        print(f'\nEfeito: {player.habs["habilidade" + str(habilidade1)]["efeito"]}')

      except:
        pass

      try:
        print(
          f'\nQuantidade minima de Acertos: {player.habs["habilidade" + str(habilidade1)]["quantiamin"]}\nQuantidade Maxima de Acertos: {player.habs["habilidade" + str(habilidade1)]["quantiamax"]}'
        )

      except:
        pass
      habilidade1 += 1

    except:
      break
  try:
    equip = int(input('\n            -->'))
    if equip > habilidades:
      s('clear')
      print(inva)
      sleep(2)
      s('clear')
      skillequip()
    elif equip == 1:
      s('clear')
      statjanel()
    elif equip <= 0:
      s('clear')
      print(inva)
      sleep(2)
      s('clear')
      skillequip()
    else:
      equip -= 1
      troca = input(
        'Qual habilidade você deseja trocar por esta que você escolheu?, 1/2/3'
      )
      if troca == '1':
        try:
          antiga = player.hab1
          player.hab1 = player.habs['habilidade' + str(equip)]
          player.habs['habilidade' + str(equip)] = antiga
        except:
          s('clear')
          print('A Habilidade escolhida é inexistente')
          sleep(3)
          s('clear')
          skillequip()
      elif troca == '2':
        try:
          antiga = player.hab2
          player.hab2 = player.habs['habilidade' + str(equip)]
          player.habs['habilidade' + str(equip)] = antiga
        except:
          s('clear')
          print('A Habilidade escolhida é inexistente')
          sleep(3)
          s('clear')
          skillequip()
      elif troca == '3':
        try:
          antiga = player.hab3
          player.hab3 = player.habs['habilidade' + str(equip)]
          player.habs['habilidade' + str(equip)] = antiga
        except:
          s('clear')
          print('A Habilidade escolhida é inexistente')
          sleep(3)
          s('clear')
          skillequip()

  except:
    s('clear')
    print('Você insiriu algo Invalido')
    sleep(3)
    s('clear')
    skillequip()


def statjanel():
  global player
  janel = input(cores.negrito + f'''
        Janela de Status

        Nivel: {player.nivel}
    Exp: {player.exp['exp']}/{player.exp['expup']}

Vida: {player.vida['vida']}/{player.vida['vidamax']} (V)

Mana: {player.mana['mana']}/{player.mana['manamax']} (M)

Poder: {player.poder} (P)
Buff de Poder: {player.poder*5}%

        Pontos de Status: {player.statpoint}

(1) Equipar Habilidades
(2) Voltar

        -->''')
  if janel.upper() == 'V' and player.statpoint >= 1:
    s('clear')
    player.vida['vida'] += 5
    player.vida['vidamax'] += 5
    player.statpoint -= 1
    statjanel()
  elif janel.upper() == 'M' and player.statpoint >= 1:
    s('clear')
    player.mana['mana'] += 5
    player.mana['manamax'] += 5
    player.statpoint -= 1
    statjanel()
  elif janel.upper() == 'P' and player.statpoint >= 1:
    s('clear')
    player.poder += 1
    player.statpoint -= 1
    statjanel()
  elif janel == '1':
    s('clear')
    skillequip()
  elif janel == '2':
    s('clear')
    lugarsalvo()
  else:
    s('clear')
    print(inva)
    sleep(1.5)
    s('clear')
    statjanel()


def convert():
  global player
  quan = input('''
    (1) Moedas de Cobre -> Moeda de Prata
    (2) Moedas de Prata -> Moedas de Cobre
    (3) Moedas de Prata -> Moedas de Ouro
    (4) Moedas de Ouro -> Moedas de Prata
    (5) Informaçoes
    (6) Voltar
    
            -->''')
  logs = [
    1000,
    2000,
    3000,
    4000,
    5000,
    6000,
    7000,
    8000,
    9000,
    10000,
    11000,
    12000,
    13000,
    14000,
    15000,
    16000,
    17000,
    18000,
    19000,
    20000,
  ]
  if quan == '1' and player.coins['moedacobre'] >= 1000:
    s('clear')
    quantia = input(
      'Insira a quantidade de moedas de cobre que você quer convertar para Moedas de prata -->'
    )
    quantia = sub(' ','', quantia)
    certo = quantia.isnumeric()
    if certo == False:
      s('clear')
      print(cores.yellow + 'Insira apenas numeros' + cores.negrito)
      sleep(1.5)
      convert()
    else:
      quantia = int(quantia)
    if quantia > player.coins['moedacobre']:
      print('isto é mais do que voce tem!!')
      sleep(1.5)
      s('clear')
      convert()
    elif quantia < 1000:
      print(
        'Precisa de no minimo 1000 moedas de cobre para converter para uma de prata'
      )
      sleep(1.5)
      s('clear')
      convert()
    elif quantia not in logs:
      print(
        'a cada 1000 moedas de cobre é possivel converter para uma de prata, numeros como: 1590, não são validos para trocar, agora numeros como: 1000, 2000, 3000 etc são validos'
      )
      sleep(1.5)
      s('clear')
      convert()
    else:
      player.coins['moedacobre'] -= quantia
      quantia = str(quantia)
      if len(quantia) == 4:
        quantia = int(quantia)
        bn = [int(a) for a in str(quantia)]
        player.coins['moedaprata'] += bn[0]
      elif len(quantia) == 5:
        quantia = int(quantia)
        bn = [int(a) for a in str(quantia)]
        player.coins['moedaprata'] += bn[1]
        player.coins['moedaprata'] += bn[0] * 10
      s('clear')
      print('Moedas convertidas com sucesso')
      sleep(1.5)
      s('clear')
      convert()

  elif quan == '2' and player.coins['moedaprata'] >= 1:
    s('clear')
    quantia = input(
      'Insira a quantidade de moedas de prata que você quer convertar para Moedas de cobre -->'
    )
    quantia = sub(' ', '', quantia)
    certo = quantia.isnumeric()
    if certo == False:
      s('clear')
      print(cores.yellow + 'Insira apenas numeros' + cores.negrito)
      sleep(1.5)
      convert()
    else:
      quantia = int(quantia)
    if quantia > player.coins['moedaprata']:
      print('isto é mais do que voce tem!!')
      sleep(1.5)
      s('clear')
      convert()
    elif quantia < 1:
      print(
        'Precisa de no minimo 1 moeda de prata para converter por 1000 moedas de cobre'
      )
      sleep(1.5)
      s('clear')
      convert()
    else:
      player.coins['moedaprata'] -= quantia
      player.coins['moedacobre'] += quantia * 1000
      s('clear')
      print('Moedas convertidas com sucesso')
      sleep(1.5)
      s('clear')
      convert()
  elif quan == '3' and player.coins['moedaprata'] >= 1000:
    s('clear')
    quantia = input(
      'Insira a quantidade de moedas de prata que você quer convertar para Moedas de ouro -->'
    )
    quantia = sub(' ', '', quantia)
    certo = quantia.isnumeric()
    if certo == False:
      s('clear')
      print(cores.yellow + 'Insira apenas numeros' + cores.negrito)
      sleep(1.5)
      convert()
    else:
      quantia = int(quantia)
    if quantia > player.coins['moedaprata']:
      print('isto é mais do que voce tem!!')
      sleep(1.5)
      s('clear')
      convert()
    elif quantia < 1000:
      print(
        'Precisa de no minimo 1000 moedas de prata para converter para uma de ouro'
      )
      sleep(1.5)
      s('clear')
      convert()
    elif quantia not in logs:
      print(
        'a cada 1000 moedas de prata é possivel converter para uma de ouro, numeros como: 1590, não são validos para trocar, agora numeros como: 1000, 2000, 3000 etc são validos'
      )
      sleep(1.5)
      s('clear')
      convert()
    else:
      player.coins['moedaprata'] -= quantia
      quantia = str(quantia)
      if len(quantia) == 4:
        quantia = int(quantia)
        bn = [int(a) for a in str(quantia)]
        player.coins['moedaouro'] += bn[0]
      elif len(quantia) == 5:
        quantia = int(quantia)
        bn = [int(a) for a in str(quantia)]
        player.coins['moedaouro'] += bn[1]
        player.coins['moedaouro'] += bn[0] * 10
      s('clear')
      print('Moedas convertidas com sucesso')
      sleep(1.5)
      s('clear')
      convert()
  elif quan == '4' and player.coins['moedaouro'] >= 1:
    s('clear')
    quantia = input(
      'Insira a quantidade de moedas de ouro que você quer convertar para Moedas de prata -->'
    )
    quantia = sub(' ', '', quantia)
    certo = quantia.isnumeric()
    if certo == False:
      s('clear')
      print(cores.yellow + 'Insira apenas numeros' + cores.negrito)
      sleep(1.5)
      convert()
    else:
      quantia = int(quantia)
    if quantia > player.coins['moedaouro']:
      print('isto é mais do que voce tem!!')
      sleep(1.5)
      s('clear')
      convert()
    elif quantia < 1:
      print(
        'Precisa de no minimo 1 moeda de ouro para converter por 1000 moedas de prata'
      )
      sleep(1.5)
      s('clear')
      convert()
    else:
      player.coins['moedaouro'] -= quantia
      player.coins['moedaprata'] += quantia * 1000
      s('clear')
      print('Moedas convertidas com sucesso')
      sleep(1.5)
      s('clear')
      convert()
  elif quan == '5':
    print('''
1000 Moedas de Cobre para cada 1 moeda de prata
1 Moeda de Prata = 1000 Moedas de Cobre
1000 Moedas de Prata para cada 1 moeda de ouro
1 moeda de ouro = 1000 Moedas de prata''')
    sleep(3)
    s('clear')
    convert()
  elif quan == '6':
    s('clear')
    bal()
  else:
    print(
      'Você não tem moedas o suficiente para converter ou voce insiriu algo invalido'
    )
    sleep(2)
    s('clear')
    convert()


def verificarmissao(monstro):
  global player
  if monstro['nome'] == player.missao['monstro']:
    player.missao['quantia'] += 1
  if player.missao['quantia'] >= player.missao['quantiamatar']:
    player.missao['quantia'] = 0
    player.missao['monstro'] = ''
    player.exp['exp'] += player.missao['recompensa']['exp']
    if player.missao['recompensa']['coinstipo'] == 'Moedas de Cobre':
      player.coins['moedacobre'] += player.missao['recompensa']['coins']
    print(cores.blue + 'Voce completou sua missão' + cores.negrito)
    print(
      f'Você ganhou {player.missao["recompensa"]["exp"]} de Exp e {player.missao["recompensa"]["coins"]} de {player.missao["recompensa"]["coinstipo"]}'
    )
    sleep(2.5)


missao = {}
no = 1


def guilda():
  global player, missao, no
  if no == 1:
    no = 0
    monsto = ['Slime', 'Kobold', 'Lobo']
    if player.bossderrotado['Slime Gigante'] == 'sim':
      monsto = ['Slime', 'Kobold', 'Lobo', 'Kobold Mago', 'Goblin', 'Esqueleto']
    missao = {
      'missao1': {
        'monstro': choice(monsto),
        'quantiamatar': randint(1, 5),
        'recompensa': {
          'coins': 0,
          'coinstipo': '',
          'exp': 0
        }
      },
      'missao2': {
        'monstro': choice(monsto),
        'quantiamatar': randint(1, 5),
        'recompensa': {
          'coins': 0,
          'coinstipo': '',
          'exp': 0
        }
      },
      'missao3': {'monstro': choice(monsto), 'quantiamatar': randint(1, 5), 'recompensa': {'coins': 0, 'coinstipo': '', 'exp': 0}}}

    misso = 1
    while True:
      if misso > 3:
        break
      if missao['missao' + str(misso)]['monstro'] == 'Slime':
        missao['missao' + str(misso)]['recompensa']['coins'] = missao['missao' + str(misso)]['quantiamatar'] * 5
        missao['missao' + str(misso)]['recompensa']['exp'] = missao['missao' + str(misso)]['quantiamatar'] * 4
        missao['missao' + str(misso)]['recompensa']['coinstipo'] = 'Moedas de Cobre'
      elif missao['missao' + str(misso)]['monstro'] == 'Kobold':
        missao['missao' + str(misso)]['recompensa']['coins'] = missao['missao' + str(misso)]['quantiamatar'] * 7
        missao['missao' + str(misso)]['recompensa']['exp'] = missao['missao' + str(misso)]['quantiamatar'] * 6
        missao['missao' + str(misso)]['recompensa']['coinstipo'] = 'Moedas de Cobre'
      elif missao['missao' + str(misso)]['monstro'] == 'Lobo':
        missao['missao' + str(misso)]['recompensa']['coins'] = missao['missao' + str(misso)]['quantiamatar'] * 9
        missao['missao' + str(misso)]['recompensa']['exp'] = missao['missao' + str(misso)]['quantiamatar'] * 8
        missao['missao' + str(misso)]['recompensa']['coinstipo'] = 'Moedas de Cobre'
      elif missao['missao' + str(misso)]['monstro'] == 'Goblin':
        missao['missao' + str(misso)]['recompensa']['coins'] = missao['missao' + str(misso)]['quantiamatar'] * 11
        missao['missao' + str(misso)]['recompensa']['exp'] = missao['missao' + str(misso)]['quantiamatar'] * 10
        missao['missao' + str(misso)]['recompensa']['coinstipo'] = 'Moedas de Cobre'
      elif missao['missao' + str(misso)]['monstro'] == 'Esqueleto':
        missao['missao' + str(misso)]['recompensa']['coins'] = missao['missao' + str(misso)]['quantiamatar'] * 13
        missao['missao' + str(misso)]['recompensa']['exp'] = missao['missao' + str(misso)]['quantiamatar'] * 12
        missao['missao' + str(misso)]['recompensa']['coinstipo'] = 'Moedas de Cobre'
      elif missao['missao' + str(misso)]['monstro'] == 'Kobold Mago':
        missao['missao' + str(misso)]['recompensa']['coins'] = missao['missao' + str(misso)]['quantiamatar'] * 15
        missao['missao' + str(misso)]['recompensa']['exp'] = missao['missao' + str(misso)]['quantiamatar'] * 14
        missao['missao' + str(misso)]['recompensa']['coinstipo'] = 'Moedas de Cobre'
      misso += 1

  print(f'''
                Guilda

              (1)
     ______________________
    |       Missao 1       |
     Matar: {missao["missao1"]["quantiamatar"]} {missao["missao1"]["monstro"]}
     Exp: {missao["missao1"]["recompensa"]["exp"]}
     Coins: {missao["missao1"]["recompensa"]["coins"]} {missao["missao1"]["recompensa"]["coinstipo"]}
    |______________________|
    
              ''')
  print(f'''
             (2)
     ______________________
    |       Missao 2       |
     Matar: {missao["missao2"]["quantiamatar"]} {missao["missao2"]["monstro"]}
     Exp: {missao["missao2"]["recompensa"]["exp"]}
     Coins: {missao["missao2"]["recompensa"]["coins"]} {missao["missao2"]["recompensa"]["coinstipo"]}
    |______________________|

              ''')
  ta = input(f'''
             (3)
     ______________________
    |       Missao 3       |
     Matar: {missao["missao3"]["quantiamatar"]} {missao["missao3"]["monstro"]}
     Exp: {missao["missao3"]["recompensa"]["exp"]}
     Coins: {missao["missao3"]["recompensa"]["coins"]} {missao["missao3"]["recompensa"]["coinstipo"]}
    |______________________|                                                                                            
                                                                                                
    (4) Renovar Missoes, 100 moedas de cobre
    (5) Abandonar Missao
    (6) Voltar
               -->''')
  if ta == '1' and player.missao['monstro'] == '':
    player.missao['monstro'] = missao['missao1']['monstro']
    player.missao['quantiamatar'] = missao['missao1']['quantiamatar']
    player.missao['recompensa'] = missao['missao1']['recompensa']
    print(cores.pink + 'Voce pegou a missao 1' + cores.negrito)
    sleep(1.5)
    s('clear')
    guilda()
  elif ta == '2' and player.missao['monstro'] == '':
    player.missao['monstro'] = missao['missao2']['monstro']
    player.missao['quantiamatar'] = missao['missao2']['quantiamatar']
    player.missao['recompensa'] = missao['missao2']['recompensa']
    print(cores.pink + 'Voce pegou a missao 2' + cores.negrito)
    sleep(1.5)
    s('clear')
    guilda()
  elif ta == '3' and player.missao['monstro'] == '':
    player.missao['monstro'] = missao['missao3']['monstro']
    player.missao['quantiamatar'] = missao['missao3']['quantiamatar']
    player.missao['recompensa'] = missao['missao3']['recompensa']
    print(cores.pink + 'Voce pegou a missao 3' + cores.negrito)
    sleep(1.5)
    s('clear')
    guilda()
  elif ta == '4':
    if player.coins['moedacobre'] >= 100:
      s('clear')
      no = 1
      player.coins['moedacobre'] -= 100
      print('Missoes Renovadas com sucesso')
      sleep(1.5)
      s('clear')
      guilda()
    else:
      s('clear')
      print(cores.yellow + 'Você não tem moedas de cobre o suficiente' +
            cores.yellow)
      sleep(1.5)
      s('clear')
      guilda()
  elif ta == '5':
    player.missao['monstro'] = ''
    print(cores.yellow + 'Missao abandonada' + cores.negrito)
    sleep(1.5)
    s('clear')
    guilda()
  elif ta == '6':
    s('clear')
    lugarsalvo()
  else:
    s('clear')
    print(cores.red + 'Voce ja pegou uma missao ou insiriu algo invalido' +
          cores.negrito)
    sleep(1.5)
    s('clear')
    guilda()


def bal():
  global player
  bau = input(f'''
        Saldo
Moedas de Cobre: {player.coins['moedacobre']}

Moedas de Prata: {player.coins['moedaprata']}

Moedas de Ouro: {player.coins['moedaouro']}

(1) Converter Moedas
(2) Voltar
    
      -->''')
  if bau == '1':
    s('clear')
    convert()
  elif bau == '2':
    s('clear')
    lugarsalvo()
  else:
    s('clear')
    print(inva)
    sleep(1.5)
    s('clear')
    bal()


def casa():
  global player
  player.casa['descansar'] = player.nivel
  escolh = input('''
          Casa
    (1) Descansar [se recupera de literalmente tudo, só pode ser usado uma vez a cada nivel upado]
    (2) Comida [Personagem precisa estar com fome]
    (3) Voltar

           -->''')
  if escolh == '1':
    if player.casa['descansar'] > player.casa['descansados']:
      player.casa['descansados'] += 1
      logs = ('Descansando.', 'Descansando..', 'Descansando...',
              'Descansando.', 'Descansando..', 'Descansando...')
      for i in logs:
        s('clear')
        print(i)
        sleep(0.5)
      player.vida['vida'] = player.vida['vidamax']
      player.mana['mana'] = player.mana['manamax']
      player.status['efeito'] = ''
      print('Você se recuperou de tudo!')
      sleep(1.5)
      s('clear')
      casa()
    else:
      s('clear')
      print('Você nao pode descansar')
      sleep(1.5)
      s('clear')
      casa()
  elif escolh == '2':
    if player.casa['fome'] < 3:
      print('As comidas que você tem são:')
      if player.casa['comida']['Bife'] >= 1:
        print(f'{player.casa["comida"]["Bife"]} Bifes')
      if player.casa['comida']['Frango'] >= 1:
        print(f'{player.casa["comida"]["Frango"]} Frango')
      if player.casa['comida']['Arroz'] >= 1:
        print(f'{player.casa["comida"]["Arroz"]} potes de Arroz')
      sla123 = input('O que deseja comer? -->')
      if search('BIFE', unidecode(sla123.upper())) != None:
        player.casa['comida']['Bife'] -= 1
        player.casa['fome'] = 10
        print('Você comeu um Bife e recuperou sua fome')
        sleep(1.5)
        s('clear')
        casa()
      elif search('FRANGO', unidecode(sla123.upper())) != None:
        player.casa['comida']['Frango'] -= 1
        player.casa['fome'] = 10
        print('Você comeu um Frango e recuperou sua fome')
        sleep(1.5)
        s('clear')
        casa()
      elif search('ARROZ', unidecode(sla123.upper())) != None:
        player.casa['comida']['Arroz'] -= 1
        player.casa['fome'] = 10
        print('Você comeu um pote de Arroz e recuperou sua fome')
        sleep(1.5)
        s('clear')
        casa()
      elif search('NADA', unidecode(sla123.upper())) != None:
        print('Você não comeu nada')
        sleep(1.5)
        s('clear')
        casa()
      else:
        print(inva)
        sleep(1.5)
        s('clear')
        casa()
    else:
      s('clear')
      print('Seu personagem não está com fome')
      sleep(1.5)
      s('clear')
      casa()
  elif escolh == '3':
    s('clear')
    lugarsalvo()
  else:
    print(inva)
    sleep(1.5)
    s('clear')
    casa()


def skillsunlock():
  global player
  if player.classe == 'Mago':
    habi = input('''
        Habilidades de Mago para Desbloquar
        
(1) Voltar

Fogo do Dragão Elemental [Nivel 15] [500 moeda de cobre]  (2 para desbloquear)
Mana: 100
Dano Base: 150
Efeitos: Queimadura por 2 Turnos
Cooldown: 3 Turnos
       
                -->''')
    if habi == '1':
      s('clear')
      lugarsalvo()
    elif habi == '2':
      if player.nivel >= 15:
        if player.coins['moedacobre'] >= 500:
          haha = 1
          while True:
            try:
              if player.habs['habilidade' + str(haha)] == '':
                pass
              haha += 1
            except:
              player.habs['habilidade' + str(haha)] = {
                'nome':
                'Fogo do Dragão Elemental',
                'mana':
                100,
                'dano':
                150,
                'tipo':
                'Ataque e Efeito',
                'Efeito':
                'Queimadura',
                'turnos':
                2,
                'desc':
                'Você Conjurou uma magia para usar o poder do fogo do Dragão Elemental e usou contra o inimigo',
                'cooldown': 0,
                'cooldownmax': 3
              
              }
              break
          print(
            'Você aprendeu a habilidade Fogo do Dragão Elemental, equipe-a em Janela de Status -> Equipar Habilidades'
          )
          player.coins['moedacobre'] -= 500
        else:
          s('clear')
          print('Você não tem moedas de cobre o suficiente')
          sleep(3)
          s('clear')
          skillsunlock()
      else:
        s('clear')
        print('Você nao tem nivel o suficiente')
        sleep(3)
        s('clear')
        skillsunlock()
    else:
      s('clear')
      print(inva)
      sleep(2)
      s('clear')
      skillsunlock()
        
  elif player.classe == 'Cavaleiro':
    habi = input('''
        Habilidades de Cavaleiro para Desbloquar
        
(1) Voltar
        
Espada de Aura [Nivel 15] [500 moeda de cobre]  (2 para desbloquear)
Mana: 80
Dano Base: 180
Efeitos: Nenhum
Cooldown: 3 Turnos
        
                -->''')

    if habi == '1':
      s('clear')
      lugarsalvo()
    elif habi == '2':
      if player.nivel >= 15:
        if player.coins['moedacobre'] >= 500:
          haha = 1
          while True:
            try:
              if player.habs['habilidade' + str(haha)] == '':
                pass
              haha += 1
            except:
              player.habs['habilidade' + str(haha)] = {
                'nome':
                'Espada de Aura',
                'mana':
                80,
                'dano':
                180,
                'tipo':
                'Ataque',
                'desc':
                'Você investe sua espada com uma variante da Mana, chamada Aura que é muito mais poderosa, e ataca o inimigo',
                'cooldown': 0,
                'cooldownmax': 3
              }
              break
          print(
            'Você aprendeu a habilidade Espada de Aura, equipe-a em Janela de Status -> Equipar Habilidades'
          )
          player.coins['moedacobre'] -= 500
        else:
          s('clear')
          print('Você não tem moedas de cobre o suficiente')
          sleep(3)
          s('clear')
          skillsunlock()
      else:
        s('clear')
        print('Você nao tem nivel o suficiente')
        sleep(3)
        s('clear')
        skillsunlock()
    else:
      s('clear')
      print(inva)
      sleep(2)
      s('clear')
      skillsunlock()
  elif player.classe == 'Arqueiro':
    habi = input('''
        Habilidades de Arqueiro para Desbloquar
        
(1) Voltar
        
Flecha de Ponta Cristalizada Venenosa [Nivel 15] [500 moeda de cobre]  (2 para desbloquear)
Mana: 100
Dano Base: 150
Efeitos: Veneno por 2 Turnos
Cooldown: 3 Turnos
        
                -->''')
    if habi == '1':
      s('clear')
      lugarsalvo()
    elif habi == '2':
      if player.nivel >= 15:
        if player.coins['moedacobre'] >= 500:
          haha = 1
          while True:
            try:
              if player.habs['habilidade' + str(haha)] == '':
                pass
              haha += 1
            except:
              player.habs['habilidade' + str(haha)] = {
                'nome':
                'Flecha de Ponta Cristalizada Venenosa',
                'mana':
                100,
                'dano':
                150,
                'tipo':
                'Ataque e Efeito',
                'Efeito':
                'Veneno',
                'turnos':
                2,
                'desc':
                'Você atira uma flecha com uma ponta de cristal com veneno no oponente',
                'cooldown': 0,
                'cooldownmax': 3
              }
              break
          print(
            'Você aprendeu a habilidade Flecha de Ponta Cristalizada Venenosa, equipe-a em Janela de Status -> Equipar Habilidades'
          )
          player.coins['moedacobre'] -= 500
        else:
          s('clear')
          print('Você não tem moedas de cobre o suficiente')
          sleep(3)
          s('clear')
          skillsunlock()
      else:
        s('clear')
        print('Você nao tem nivel o suficiente')
        sleep(3)
        s('clear')
        skillsunlock()
    else:
      s('clear')
      print(inva)
      sleep(2)
      s('clear')
      skillsunlock()

def vilahabusken():
  global player, andar
  s('clear')
  player.lugar = 'vila habusken'

  opmenu = input('''
            Vila Habusken
(1) Loja
(2) Mestre de Habusken
(3) Dungeon de Habusken
(4) Inventario
(5) Casa
(6) Personagem
(7) Desbloquar Habilidades
(8) Janela de Status
(9) Guilda
(10) Curandeira
(11) Dinheiro
(0) Salvar Dados ***IMPORTANTE***

        ->''')

  if opmenu == '1':
    s('clear')
    loja()
  elif opmenu == '2':
    s('clear')
    mestrehabusken()
  elif opmenu == '3':
    s('clear')
    andar = 1
    dungeonhabusken()
  elif opmenu == '4':
    s('clear')
    inventario()
  elif opmenu == '5':
    s('clear')
    casa()
  elif opmenu == '6':
    s('clear')
    avatar()
  elif opmenu == '7':
    s('clear')
    skillsunlock()
  elif opmenu == '8':
    s('clear')
    statjanel()
  elif opmenu == '9':
    s('clear')
    guilda()
  elif opmenu == '10':
    s('clear')
    curandeira()
  elif opmenu == '11':
    s('clear')
    bal()
  elif opmenu == '0':
    print('Salvando Dados...')
    salvardados()
    sleep(2)
    print(cores.green + 'Dados salvo com sucesso' + cores.negrito)
    sleep(1.5)
    s('clear')
    vilahabusken()
  else:
    print(inva)
    sleep(1.5)
    s('clear')
    vilahabusken()


def inicio():
  global player
  print(
    '''Você era um cidadão de uma cidade no interior de Brasil, Você era um policial respeitado. Sua ultima investigação
era de uma criança desaparecida, você a encontrou mas o sequestrador ameaçava a mata-lá, jogando-a de um predio, mas para 
impedir isto você se sacrificou pela criança se jogando junto com o sequestrador em cima de um prédio de 10 andares, então
você e o sequestrador acaba morrendo, mas visto o como você era um bom policial, Deus lhe reencarnou em um mundo de fantasia
com magia, monstros, habilidades etc. Deus lhe reencarnou por bondade e deixou você aproveitar este mundo do jeito que voce quiser
neste mundo existem Dungeons, cuja origem é totalmente misteriosa, elas apenas apareceram ao mundo 1800 anos atrás, o mundo em
questão esta por volta do periodo medieval. Você acorda neste mundo com todo o conhecimento basico dele, e percebe que esta em
um corpo adulto diferente em uma casa pequena com coisas basicas, como: cama, armario etc. mas nada tecnologico como um computador
ou até mesmo uma geladeira. Você vê uma mochilha abre ela e encontra um mini saco com 100 moedas de cobre, um pouco de comida e
identidades. Você sai de sua casa e percebe que mora em uma cidade depois de ver tudo isso decide que quer virar um aventureiro e
descobrir sobre  mistério das Dungeons.
    ''')
  enter = input(cores.green + 'Aperte Enter para continuar' + cores.negrito)
  s('clear')
  while True:
    raçaescolha = input('''
        Antes de começar sua Aventura. Escolha a Raça que deseja
(1) Fada
(2) Humano
(3) Elfo
(4) Informaçoes da Raça

        ->''')
    if raçaescolha == '1':
      player.raca = {'raca': 'Fada', 'bufftipo': 'Esquiva', 'valor': 6}
      player.esquiva = player.raca['valor']
      break
    elif raçaescolha == '2':
      player.raca = {'raca': 'Humano', 'bufftipo': 'Poder', 'valor': 10}
      break
    elif raçaescolha == '3':
      player.raca = {'raca': 'Elfo', 'bufftipo': 'Exp', 'valor': 25}
      break
    elif raçaescolha == '4':
      print('''
                Informaçoes
Fada: Buff de Esquiva para 16,5%
Humano: Buff de Poder, Aumenta 10% do Dano
Elfo: Buff de Exp, Aumenta 25% de Exp ganho ''')

      input(cores.green + 'Enter para continuar' + cores.negrito)
      s('clear')
    else:
      print(inva)
      sleep(1.5)
      s('clear')
  while True:
    classeescolher = input('''
            Agora vamos Escolher sua Classe
(1) Mago
(2) Cavaleiro
(3) Arqueiro
(4) Informaçoes

            ->''')
    if classeescolher == '1':
      player.classe = 'Mago'
      player.hab1 = {
        'nome':
        'Missil Magico',
        'mana':
        15,
        'dano':
        15,
        'tipo':
        'Ataque',
        'desc':
        'Conjurou uma bola de mana e jogou no oponente a uma velocidade gigantesca',
        'cooldown': 0,
        'cooldownmax': 0
      }
      player.hab2 = {
        'nome': 'Chamas',
        'mana': 25,
        'dano': 30,
        'tipo': 'Ataque e Efeito',
        'Efeito': 'Queimadura',
        'turnos': 3,
        'desc': 'Conjurou chamas e atira elas em direção ao Alvo',
        'cooldown': 0,
        'cooldownmax': 2
      }
      player.hab3 = {
        'nome':
        'Raio',
        'mana':
        50,
        'dano':
        80,
        'tipo':
        'Ataque e Efeito',
        'Efeito':
        'Paralisia',
        'turnos':
        1,
        'desc':
        'Reune um poder magico para convocar um Raio dos céus para cair em cima do inimigo',
        'cooldown': 0,
        'cooldownmax': 3
      }
      player.equipado['arma'] = {'nome': 'Cajado Basico', 'buff': 0}
      break
    elif classeescolher == '2':
      player.classe = 'Cavaleiro'
      player.hab1 = {
        'nome': 'Investida',
        'mana': 15,
        'dano': 15,
        'tipo': 'Ataque',
        'desc': 'Faz uma rapida investida no oponente e o ataca',
        'cooldown': 0,
        'cooldownmax': 0
      }
      player.hab2 = {
        'nome': 'Corte Fatal',
        'mana': 20,
        'dano': 25,
        'tipo': 'Ataque e Efeito',
        'turnos': 3,
        'Efeito': 'Sangramento',
        'desc': 'Faz um corte muito profundo e grande nas costas do oponente',
        'cooldown': 0,
        'cooldownmax': 2
      }
      player.hab3 = {
        'nome':
        'Espada Magica',
        'mana':
        45,
        'dano':
        100,
        'tipo':
        'Ataque',
        'desc':
        'Dá um golpe com uma espada investida com Mana fazendo a espada ficar muito mais forte',
        'cooldown': 0,
        'cooldownmax': 2
      }
      player.equipado['arma'] = {'nome': 'Espada Basica', 'buff': 0}
      break
    elif classeescolher == '3':
      player.classe = 'Arqueiro'
      player.hab1 = {
        'nome': 'Flecha Rapida',
        'mana': 20,
        'dano': 20,
        'tipo': 'Ataque',
        'desc': 'Atira uma flecha rapida que crava no peito do inimigo',
        'cooldown': 0,
        'cooldownmax': 0
      }
      player.hab2 = {
        'nome': 'Flecha Tripla',
        'mana': 30,
        'dano': 20,
        'tipo': 'Multiplo Ataque',
        'quantiamin': 1,
        'quantiamax': 3,
        'desc': 'Atira tres flechas de uma vez no inimigo',
        'cooldown': 0,
        'cooldownmax': 2
      }
      player.hab3 = {
        'nome':
        'Chuva de Flecha',
        'mana':
        55,
        'dano':
        20,
        'tipo':
        'Multiplo Ataque',
        'quantiamin':
        5,
        'quantiamax':
        8,
        'desc':
        'Atira 8 flechas em cima do oponente fazendo elas cairem e criarem uma chuva de flechas',
        'cooldown': 0,
        'cooldownmax': 3
      }
      player.equipado['arma'] = {'nome': 'Arco Basico', 'buff': 0}
      break
    elif classeescolher == '4':
      print('''
        Informaçoes
Mago:
Habilidade 1: Missil Magico, Conjura uma bola de mana e joga no oponente a uma velocidade gigantesca, 10 de Mana Gasta e dano base de 15
Habilidade 2: Chamas, Conjura chamas e atira elas em direção ao Alvo causando Queimadura, 20 de mana gasta e 30 de dano base, 2 turnos de cooldown
Habilidade 3: Raio, Reune um poder magico para convocar um Raio dos céus para cair em cima do inimigo, o deixando com paralisia, 50 de mana gasta e 80 de dano base, 3 turnos de cooldown


Cavaleiro:
Habilidade 1: Investida, Faz uma rapida investida no oponente e o ataca, 10 de mana gasta e 15 de dano base
Habilidade 2: Corte Fatal, Faz um corte muito profundo e grande nas costas do oponente, Deixando o Oponente com Sangramento, 15 de mana gasta e 25 de dano base, 2 turnos de cooldown
Habilidade 3: Espada Magica, Dá um golpe com uma espada investida com Mana fazendo a espada ficar muito mais forte, 45 de mana gasta e 100 de dano base, 2 turnos de cooldown


Arqueiro:
Habilidade 1: Flecha Rapida, Atira uma flecha rapida que crava no peito do inimigo, 15 de mana gasta e 20 de dano base
Habilidade 2: Flecha Tripla, Atira tres flechas de uma vez, 25 de mana gasta e 15 de dano base por flecha, 2 turnos de cooldown
Habilidade 3: Chuva de Flecha, Atira 10 flechas em cima do oponente fazendo elas cairem e criarem uma chuva de flechas, 60 de mana gasta e 15 de dano base por flecha, 3 turnos de cooldown
''')
      pause = input('precione enter para continuar')
      s('clear')
    else:
      print(inva)
      sleep(1.5)
      s('clear')

  vilahabusken()


def teste():
  con = input(cores.negrito + '''
Ola, o que deseja fazer
(1) Registrar
(2) Logar

    >''')
  if con == '1':
    nome = input('Nome: ')
    senha = input('Senha: ')
    print('Criando a conta...')
    sleep(2)
    registrar(nome, senha)
  elif con == '2':
    logar()
  else:
    print(inva)
    sleep(1.5)
    s('clear')
    teste()


teste()
