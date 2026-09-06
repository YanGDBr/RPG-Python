"""Orquestração do jogo: seleção de save slot, criação de personagem e o loop
principal (vila -> loja/dungeon/status/etc). Tudo aqui é loop de verdade —
nada de função chamando a si mesma pra sempre feito o jogo original.
"""

import sys
import time

from . import persistencia
from .config import DIRETORIO_BACKUPS, INTERVALO_AUTOSAVE_SEGUNDOS, Cor
from .dados.classes import CLASSES
from .dados.dungeons import DUNGEONS
from .dados.especializacoes import NIVEL_MINIMO_ESPECIALIZACAO
from .dados.itens import ITENS_CONSUMIVEIS, POCOES, POCOES_CRAFTADAS
from .dados.mapas_mundo import MAPA_ILYRATH, MAPA_VETHGARD
from .dados.npcs import NPCS
from .dados.racas import RACAS
from .entrada import menu as menu_padrao
from .entrada import pedir_texto, perguntar_sim_nao
from .interface import barra, cabecalho, limpar_tela, ljust_visivel
from .modelos.personagem import Personagem
from .persistencia import carregar_slots, salvar_slots
from .sistemas import cidade, equipamento, exploracao, inventario, loja, mundo

HISTORIA_QUEDA = """Você era policial civil numa cidade pequena do interior, Santa Rosa do Almeida — do tipo
onde todo mundo conhece todo mundo. Seu último caso foi o sequestro de Bianca, uma menina de oito anos,
levada por um homem que a cidade toda conhecia como "estranho, mas inofensivo" — até não ser mais. Você a
encontrou no telhado do prédio mais alto da cidade, minutos depois dele ameaçar, por telefone, jogá-la lá de
cima.

Não teve negociação. Você teve menos de dois segundos entre ver o movimento do braço dele e agir — só se
jogou pra puxar os dois de volta da mureta. Conseguiu empurrar Bianca de volta pro telhado. Vocês dois
caíram, dez andares.

Bianca sobreviveu. Você morreu antes de chegar ao chão — ou melhor: algo decidiu que você não precisava
chegar ao chão."""

ORDINAEL_PARTE_1 = """Você não precisa ter medo. A dor já ficou pra trás — junto com o corpo, junto com o
prédio, junto com o nome que os outros gritavam enquanto você caía.

Eu vi o que você fez. Vi você escolher, num espaço de tempo pequeno demais pra chamar de escolha, salvar uma
vida que não era a sua. Isso é raro. Mais raro do que você imagina. A maioria hesita — só um instante, só o
suficiente. Você não hesitou.

Por isso estou aqui. Chame-me do que quiser — Deus serve, se te dá conforto. Existem nomes mais antigos, mas
nenhum vai significar nada pra você ainda.

Eu não posso devolver o que você perdeu. Mas posso te dar algo novo: um corpo, um mundo, uma chance de viver
sem o peso de tudo que veio antes. Existem formas diferentes de se começar de novo — cada uma com seus
próprios dons, e seus próprios preços. Escolha o molde que mais soar como você."""

ORDINAEL_PARTE_2 = """E dentro desse molde, existem caminhos — de força, de intelecto, de pontaria. Nenhum é
superior. Todos serão testados."""

ORDINAEL_PARTE_3 = """Uma última coisa, antes de te soltar nesse mundo: eu vou estar observando. Não por
desconfiança — por cuidado. Quero ver o que você faz com essa segunda vida. Quero ver até onde ela te leva."""

EPILOGO_ABISMO = """Com o Kraken Ancestral derrotado, as águas do Abismo Submerso finalmente se aquietam. Você
não sabe dizer por quê, mas sente que Ilyrath ainda guarda um último problema — maior que qualquer coisa que
você já enfrentou. Os mapas mais antigos de Habusken marcam um lugar ao norte, a Cratera de Vhalos, só com
um aviso: "não ir". Ninguém explica o porquê. Talvez seja hora de descobrir."""

EPILOGO_VASHTAR = """O cristal negro no peito de Vashtar se estilhaça com um som que não devia existir — não
um estrondo, um silêncio que dói. Por uma fração de segundo, você sente algo se soltar: um sinal, uma
assinatura, um grito atravessando a realidade inteira num piscar de olhos.

Vashtar cai. Sob a coroa cinzenta e mil e duzentos anos de poder que nunca foram dele, resta só um homem —
o primeiro campeão de Ilyrath, o primeiro a vencer tudo, o primeiro a pagar por isso.

Ilyrath está livre. Você derrotou o Rei Cinza. Por um segundo, e só um segundo, você sentiu como se alguém —
ou algo — enorme tivesse aberto os olhos em algum lugar muito, muito longe. E então, tão rápido quanto veio,
a sensação passa — e tudo que resta é o silêncio de uma cratera finalmente vazia."""

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
  opcoes = ([_caixa_slot(i, slots[i]) for i in range(len(slots))]
            + ['Exportar Backup', 'Importar Backup', 'Sair do jogo'])
  return menu_padrao(titulo, opcoes, com_voltar=False)


def _exportar_backup_ui():
  limpar_tela()
  try:
    destino = persistencia.exportar_backup()
    print(f'{Cor.VERDE}Backup criado com sucesso!{Cor.RESET}')
    print(f'Local: {destino}')
  except FileNotFoundError as erro:
    print(f'{Cor.VERMELHO}{erro}{Cor.RESET}')
  input('\nEnter para continuar...')


def _importar_backup_ui(slots):
  limpar_tela()
  backups = persistencia.listar_backups()
  if not backups:
    print(f'{Cor.VERMELHO}Nenhum backup encontrado em {DIRETORIO_BACKUPS}.{Cor.RESET}')
    input('\nEnter para continuar...')
    return slots

  escolha = menu_padrao(
      'Escolha um backup para restaurar — isso substitui TODOS os slots atuais:',
      [caminho.name for caminho in backups])
  if escolha is None:
    return slots

  backup_escolhido = backups[escolha]
  if not perguntar_sim_nao(f'Tem certeza? Isso substitui os saves atuais por "{backup_escolhido.name}".'):
    return slots

  try:
    persistencia.importar_backup(backup_escolhido)
  except (OSError, ValueError) as erro:
    limpar_tela()
    print(f'{Cor.VERMELHO}Erro ao importar: {erro}{Cor.RESET}')
    input('\nEnter para continuar...')
    return slots

  limpar_tela()
  print(f'{Cor.VERDE}Backup restaurado com sucesso!{Cor.RESET}')
  input('\nEnter para continuar...')
  return persistencia.carregar_slots()


def _criar_personagem():
  limpar_tela()
  print(HISTORIA_QUEDA)
  input('\nAperte Enter para continuar...')

  limpar_tela()
  print(ORDINAEL_PARTE_1)
  input('\nAperte Enter para continuar...')

  nome = pedir_texto('\nEscolha o nome do seu novo corpo: -->')
  personagem = Personagem(nome=nome)

  nomes_racas = list(RACAS.keys())
  while True:
    escolha = menu_padrao('Escolha o molde que mais soa como você',
                           nomes_racas + ['Ver informações'], com_voltar=False)
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

  limpar_tela()
  print(ORDINAEL_PARTE_2)
  input('\nAperte Enter para continuar...')

  nomes_classes = list(CLASSES.keys())
  while True:
    escolha = menu_padrao('Escolha seu caminho', nomes_classes + ['Ver informações'], com_voltar=False)
    if escolha == len(nomes_classes):
      limpar_tela()
      print('\n'.join(f'{c.nome}: {c.descricao}' for c in CLASSES.values()))
      input('Enter para continuar...')
      continue
    personagem.classe = nomes_classes[escolha]
    break

  limpar_tela()
  print(ORDINAEL_PARTE_3)
  input('\nAperte Enter para continuar...')

  classe = CLASSES[personagem.classe]
  personagem.habilidades_aprendidas = list(classe.habilidades_iniciais)
  personagem.habilidades_equipadas = list(classe.habilidades_iniciais)
  personagem.local = 'vila'
  return personagem


def _processar_morte_se_necessario(personagem):
  """A punição de morte (perder 1 nível, metade das moedas, voltar com pouca
  vida/mana/fome) já foi aplicada na hora, dentro de `verificar_morte` — isso
  só limpa o sinalizador antes de mostrar a próxima tela."""
  personagem.morto = False


_estado_autosave = {'ultimo': None}


def _talvez_autosalvar(personagem, slots):
  """Salva sozinho a cada INTERVALO_AUTOSAVE_SEGUNDOS, sem interromper o
  jogador — verificado nos loops principais (vila, dungeon, mundo aberto).
  Silencioso de propósito: como a tela é limpa a cada troca de menu, qualquer
  aviso impresso aqui desapareceria antes de dar tempo de ler."""
  agora = time.monotonic()
  if _estado_autosave['ultimo'] is None:
    _estado_autosave['ultimo'] = agora
    return
  if agora - _estado_autosave['ultimo'] >= INTERVALO_AUTOSAVE_SEGUNDOS:
    salvar_slots(slots)
    _estado_autosave['ultimo'] = agora


def _descricao_pocao(nome):
  pocao = POCOES.get(nome) or POCOES_CRAFTADAS.get(nome)
  return f'+{pocao.valor} {pocao.efeito}' if pocao else ''


def _tela_inventario(personagem):
  while True:
    nomes_pocoes = [nome for nome, qtd in personagem.pocoes.items() if qtd > 0]
    nomes_itens = [nome for nome, qtd in personagem.inventario.items() if qtd > 0]
    opcoes = [f'Poção de {nome} x{personagem.pocoes[nome]} ({_descricao_pocao(nome)})'
              for nome in nomes_pocoes]
    opcoes += [f'{nome} x{personagem.inventario[nome]}'
               + (f' ({ITENS_CONSUMIVEIS[nome].descricao})' if nome in ITENS_CONSUMIVEIS else '')
               for nome in nomes_itens]
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
  ecrans = [loja.loja_acessorios, loja.loja_itens_consumiveis, loja.loja_comidas, loja.loja_pocoes,
            loja.loja_equipamentos, loja.loja_armaduras, loja.loja_ofertas_do_dia]
  while True:
    opcoes = ['Acessórios', 'Itens', 'Comida', 'Poções', 'Equipamentos', 'Armaduras',
              f'{Cor.AMARELO}Ofertas do Dia{Cor.RESET}']
    escolha = menu_padrao(f'{equipamento.resumo_status(personagem)}\n\nLoja', opcoes)
    if escolha is None:
      return
    ecrans[escolha](personagem)


def _tela_dungeon(personagem, dungeon_id, slots):
  dungeon = DUNGEONS[dungeon_id]
  while True:
    _talvez_autosalvar(personagem, slots)
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
        _processar_morte_se_necessario(personagem)
        return
    elif acao == 'Inventário':
      _tela_inventario(personagem)
    elif acao == 'Descer de andar':
      personagem.andar_atual[dungeon_id] -= 1
    elif acao == 'Subir de andar':
      personagem.andar_atual[dungeon_id] += 1
      personagem.maior_andar_visitado[dungeon_id] = max(
          personagem.maior_andar_visitado.get(dungeon_id, 1), personagem.andar_atual[dungeon_id])
    elif acao == 'Sair da dungeon':
      return


_ZONAS_SELVAGENS_ILYRATH = {'F': ['Slime', 'Kobold', 'Lobo']}


def _entrar_vethgard_callback(personagem, escrever, aguardar, limpar):
  if personagem.itens_especiais.get('Selo de Habusken', 0) <= 0:
    limpar()
    escrever(f'{Cor.CINZA}O guarda da estrada barra sua passagem: "Sem o Selo de Habusken, '
             f'ninguém entra em Vethgard. Prove seu valor na dungeon de Habusken primeiro."{Cor.RESET}')
    aguardar()
    return None
  return 'vethgard'


def _entrar_cratera_callback(personagem, escrever, aguardar, limpar):
  if personagem.itens_especiais.get('Selo de Vethgard', 0) <= 0:
    limpar()
    escrever(f'{Cor.CINZA}Os mapas antigos marcam esse caminho só como "não ir". '
             f'Talvez ainda não seja hora — falta o Selo de Vethgard.{Cor.RESET}')
    aguardar()
    return None
  return 'cratera'


def _eventos_vethgard():
  return {
    'S': mundo.falar_com_npc_e_sidequest('arquivista_sorel', 'cristal_para_sorel'),
    'M': mundo.falar_com_npc_e_sidequest('orfao_mikel', 'lenco_da_familia'),
    'G': mundo.falar_com_npc('guarda_vethgard'),
    '6': mundo.abrir_bau('vethgard_bau_1', 'pocao', 'Vida', 1),
  }


def _eventos_ilyrath():
  return {
    'T': mundo.falar_com_npc_e_sidequest('velho_caminhante', 'ecos_da_cantiga'),
    'V': _entrar_vethgard_callback,
    'C': _entrar_cratera_callback,
    '1': mundo.abrir_bau('ilyrath_bau_1', 'moedas', '', 80),
    '2': mundo.abrir_bau('ilyrath_bau_2', 'material', 'Cristal Arcano', 1),
    '3': mundo.pegar_item_do_chao('ilyrath_item_3', 'material', 'Presa de Lobo', 1),
    '4': mundo.pegar_item_do_chao('ilyrath_item_4', 'especial', 'Lenço da Família de Mikel', 1),
    '5': mundo.pegar_item_do_chao('ilyrath_item_5', 'moedas', '', 40),
  }


def _tela_vethgard(personagem):
  mundo.explorar_mapa(personagem, MAPA_VETHGARD, _eventos_vethgard(), 'Vethgard')


def _tela_mapa_mundo(personagem, slots):
  eventos = _eventos_ilyrath()
  while True:
    _talvez_autosalvar(personagem, slots)
    resultado = mundo.explorar_mapa(personagem, MAPA_ILYRATH, eventos, 'Estrada de Ilyrath',
                                     zonas_selvagens=_ZONAS_SELVAGENS_ILYRATH)
    if resultado is None:
      return
    if resultado == 'vethgard':
      _tela_vethgard(personagem)
    elif resultado == 'cratera':
      _tela_dungeon(personagem, 'cratera_vhalos', slots)
      if 'Vashtar, o Rei Cinza' in personagem.chefes_derrotados and not personagem.historia_concluida:
        personagem.historia_concluida = True
        limpar_tela()
        print(EPILOGO_VASHTAR)
        input('\nAperte Enter para continuar...')


def _opcoes_e_secoes_vila(personagem):
  """Uma lista só (sem sub-telas — foi tentado categorizar em sub-menus e o
  jogador achou pior: tinha que entrar e lembrar em qual grupo cada coisa
  estava). `secoes` só organiza visualmente com cabeçalhos coloridos, sem
  adicionar nenhum nível de navegação — sobe/desce passa por cima deles."""
  opcoes = ['Dungeon de Habusken']
  if personagem.torre_arcana_liberada:
    opcoes.append('Torre Arcana')
  if personagem.abismo_submerso_liberado:
    opcoes.append('Abismo Submerso')
  opcoes += ['Mapa do Mundo', 'Guilda']
  secoes = {0: 'AVENTURA'}

  secoes[len(opcoes)] = 'CIDADE'
  opcoes += ['Loja', 'Curandeira', 'Ferreiro', 'Bancada de Trabalho', 'Saldo',
             'Mestre de Habusken', 'Conversar com o Ancião', 'Casa']

  secoes[len(opcoes)] = 'PERSONAGEM'
  opcoes += ['Personagem', 'Status', 'Desbloquear Habilidades']
  if personagem.nivel >= NIVEL_MINIMO_ESPECIALIZACAO:
    opcoes.append('Especialização')

  secoes[len(opcoes)] = 'REGISTROS'
  opcoes += ['Tutorial', 'Estatísticas', 'Mapa de Progresso', 'Diário de Conquistas']

  secoes[len(opcoes)] = 'SISTEMA'
  opcoes += ['Salvar Dados', 'Salvar e Sair']

  return opcoes, secoes


def _titulo_vila(personagem):
  cor_fome = Cor.VERMELHO if personagem.fome <= 3 else Cor.VERDE
  return (f'{Cor.BRANCO}Vila Habusken — {personagem.nome}{Cor.RESET}\n'
          f'{equipamento.resumo_status(personagem)}  '
          f'{cor_fome}Fome {personagem.fome}/10{Cor.RESET}')


def _executar_acao_vila(acao, personagem, slots):
  if acao == 'Loja':
    _tela_loja(personagem)
  elif acao == 'Mestre de Habusken':
    cidade.tela_mestre_habusken(personagem)
  elif acao == 'Conversar com o Ancião':
    npc = NPCS['anciao_habusken']
    mundo.mostrar_falas(npc.nome, npc.falas(personagem), print, lambda: input('Enter para continuar...'),
                        limpar_tela)
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
    if 'Kraken Ancestral' in personagem.chefes_derrotados:
      personagem.cratera_vhalos_liberado = True
      if not personagem.abismo_epilogo_mostrado:
        personagem.abismo_epilogo_mostrado = True
        limpar_tela()
        print(EPILOGO_ABISMO)
        input('\nAperte Enter para continuar...')
  elif acao == 'Mapa do Mundo':
    _tela_mapa_mundo(personagem, slots)
  elif acao == 'Personagem':
    cidade.tela_personagem(personagem)
  elif acao == 'Casa':
    cidade.tela_casa(personagem)
  elif acao == 'Desbloquear Habilidades':
    cidade.tela_desbloquear_habilidades(personagem)
  elif acao == 'Status':
    cidade.tela_status(personagem)
  elif acao == 'Tutorial':
    cidade.tela_tutorial(personagem)
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
  elif acao == 'Diário de Conquistas':
    cidade.tela_diario_conquistas(personagem)
  elif acao == 'Salvar Dados':
    salvar_slots(slots)
    print(f'{Cor.VERDE}Dados salvos com sucesso!{Cor.RESET}')
    input('Enter para continuar...')
  elif acao == 'Salvar e Sair':
    salvar_slots(slots)
    print(f'{Cor.VERDE}Dados salvos. Até a próxima!{Cor.RESET}')
    sys.exit()


def _tela_vila(personagem, slots):
  indice = 0
  while True:
    _talvez_autosalvar(personagem, slots)
    if personagem.morto:
      _processar_morte_se_necessario(personagem)

    opcoes, secoes = _opcoes_e_secoes_vila(personagem)
    escolha = menu_padrao(_titulo_vila(personagem), opcoes, com_voltar=False,
                           indice_inicial=indice, secoes=secoes)
    indice = escolha
    _executar_acao_vila(opcoes[escolha], personagem, slots)


def iniciar():
  slots = carregar_slots()
  personagem = None

  while personagem is None:
    limpar_tela()
    escolha = _tela_selecionar_slot(slots)
    if escolha == len(slots):
      _exportar_backup_ui()
      continue
    if escolha == len(slots) + 1:
      slots = _importar_backup_ui(slots)
      continue
    if escolha == len(slots) + 2:
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

  _processar_morte_se_necessario(personagem)
  _tela_vila(personagem, slots)
