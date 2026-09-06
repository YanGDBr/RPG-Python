"""Todas as telas da Vila Habusken que não são a loja nem a dungeon."""

import random
import string
import time

from ..config import (ATORDOAMENTO_GANHO_POR_ACERTO_FRACO, ATORDOAMENTO_LIMIAR, BONUS_CANALIZACAO_MAXIMO_PERCENTUAL,
                       BONUS_ETEN_PERCENTUAL, BONUS_POSTURA_DEFENSIVA_DANO, BONUS_POSTURA_DEFENSIVA_REDUCAO,
                       BONUS_POSTURA_OFENSIVA_DANO, BONUS_POSTURA_OFENSIVA_DANO_RECEBIDO,
                       CHANCE_CRITICO_MAXIMA, CHANCE_GRUPO_MONSTROS, CICLO_ELEMENTAL,
                       CUSTO_RENOVAR_QUADRO, CUSTOS_SLOT_ACESSORIO, CUSTOS_SLOT_HABILIDADE,
                       ENCANTAMENTO_CUSTO_PRATA_BASE, ENCANTAMENTO_INCREMENTO, ENCANTAMENTO_MATERIAL,
                       ENCANTAMENTO_MAXIMO_ARMADURA, ENCANTAMENTO_MAXIMO_ARMA, FOCO_GANHO_POR_ATAQUE,
                       FOCO_GANHO_POR_CRITICO_EXTRA, FOME_MAXIMA, FURIA_GANHA_AO_ATACAR,
                       FURIA_GANHA_AO_LEVAR_DANO, MARCADO_BONUS_DANO_PERCENTUAL_PADRAO, MAX_MISSOES_ATIVAS,
                       MULTIPLICADOR_FRAQUEZA_CICLO, MULTIPLICADOR_FRAQUEZA_ELEMENTAL,
                       MULTIPLICADOR_RESISTENCIA_CICLO, MULTIPLICADOR_RESISTENCIA_ELEMENTAL,
                       RESSONANCIA_ARCANA_BONUS_POR_STACK, RESSONANCIA_ARCANA_MAXIMA, REPUTACAO_TIERS,
                       SIMBOLOS_MINIGAME_CANALIZACAO, Cor)
from ..dados.dungeons import DUNGEONS
from ..dados.especializacoes import (ESPECIALIZACOES, ESPECIALIZACOES_POR_CLASSE,
                                      NIVEL_MINIMO_ESPECIALIZACAO)
from ..dados.habilidades import HABILIDADES, HABILIDADES_DESBLOQUEAVEIS
from ..dados.itens import (ACESSORIOS, ACESSORIOS_UNICOS_POR_NOME, ARMADURAS, ARMADURAS_UNICAS, ARMAS,
                            ARMAS_LENDARIAS)
from ..dados.receitas import RECEITAS
from ..entrada import aguardar_leitura
from ..entrada import menu as menu_padrao
from ..entrada import pedir_numero, perguntar_sim_nao
from ..interface import limpar_tela, ljust_visivel
from . import batalha, crafting as sistema_crafting
from . import economia, equipamento, inventario


def _titulo(personagem, texto):
  return f'{equipamento.resumo_status(personagem)}\n\n{texto}'


def tela_casa(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  indice = 0
  while True:
    opcoes = ['Descansar (recupera tudo, 1x por nível)', 'Comer', 'Voltar']
    escolha = ler_acao(_titulo(personagem, 'Casa'), opcoes, indice_inicial=indice)
    if escolha is None or escolha == 2:
      return
    indice = escolha
    if escolha == 0:
      if personagem.descansos_usados >= personagem.nivel:
        escrever(f'{Cor.VERMELHO}Você já descansou o máximo de vezes permitido neste nível.{Cor.RESET}')
        aguardar()
        continue
      personagem.descansos_usados += 1
      # Cura pro máximo EFETIVO (com armadura/acessório/encantamento) — curar
      # só pro máximo base ignorava qualquer bônus de vida/mana máxima.
      personagem.vida = equipamento.vida_maxima_efetiva(personagem)
      personagem.mana = equipamento.mana_maxima_efetiva(personagem)
      personagem.efeitos_ativos.clear()
      escrever(f'{Cor.VERDE}Você descansou e se recuperou completamente!{Cor.RESET}')
      aguardar()
    elif escolha == 1:
      comidas_disponiveis = [nome for nome, qtd in personagem.comidas.items() if qtd > 0]
      if not comidas_disponiveis:
        escrever(f'{Cor.VERMELHO}Você não tem nenhuma comida.{Cor.RESET}')
        aguardar()
        continue
      escolha_comida = ler_acao('O que deseja comer?', comidas_disponiveis)
      if escolha_comida is not None:
        inventario.comer(personagem, comidas_disponiveis[escolha_comida], escrever)
        aguardar()


def _custo_cura(quantidade):
  return max(1, quantidade // 5) if quantidade > 0 else 0


def _restaurar_recurso(personagem, escrever, recurso, quantidade):
  custo = _custo_cura(quantidade)
  if personagem.moeda_cobre < custo:
    escrever(f'{Cor.VERMELHO}Você não tem cobres suficientes.{Cor.RESET}')
    return False
  personagem.moeda_cobre -= custo
  if recurso == 'vida':
    personagem.vida += quantidade
  else:
    personagem.mana += quantidade
  return True


def tela_curandeira(personagem, escrever=print, ler_acao=None, entrada_texto=input, aguardar=None):
  """Curandeira reformulada: a reclamação era ter que restaurar vida e mana
  separadamente e sempre precisar digitar a quantidade exata. Agora as opções
  de topo restauram tudo de uma vez, com o custo já calculado — só quem quer
  economizar cobres restaurando uma quantidade específica precisa digitar
  algo."""
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  indice = 0
  while True:
    falta_vida = equipamento.vida_maxima_efetiva(personagem) - personagem.vida
    falta_mana = equipamento.mana_maxima_efetiva(personagem) - personagem.mana
    custo_vida = _custo_cura(falta_vida)
    custo_mana = _custo_cura(falta_mana)

    opcoes = [
      f'Restaurar tudo ({Cor.VERMELHO}vida{Cor.RESET} e {Cor.AZUL}mana{Cor.RESET}) — '
      f'{custo_vida + custo_mana} cobres',
      f'Restaurar toda a {Cor.VERMELHO}vida{Cor.RESET} — {custo_vida} cobres',
      f'Restaurar toda a {Cor.AZUL}mana{Cor.RESET} — {custo_mana} cobres',
      'Restaurar uma quantidade específica',
      'Voltar',
    ]
    escolha = ler_acao(_titulo(personagem, 'Curandeira'), opcoes, indice_inicial=indice)
    if escolha is None or escolha == 4:
      return
    indice = escolha

    if escolha in (0, 1, 2):
      cura_vida = escolha in (0, 1) and falta_vida > 0
      cura_mana = escolha in (0, 2) and falta_mana > 0
      if not cura_vida and not cura_mana:
        escrever(f'{Cor.VERMELHO}Já está no máximo.{Cor.RESET}')
        aguardar()
        continue

      custo_total = (custo_vida if cura_vida else 0) + (custo_mana if cura_mana else 0)
      if not perguntar_sim_nao(f'Isso vai custar {custo_total} cobres. Confirmar?'):
        continue
      if personagem.moeda_cobre < custo_total:
        escrever(f'{Cor.VERMELHO}Você não tem cobres suficientes.{Cor.RESET}')
        aguardar()
        continue

      if cura_vida:
        _restaurar_recurso(personagem, escrever, 'vida', falta_vida)
      if cura_mana:
        _restaurar_recurso(personagem, escrever, 'mana', falta_mana)
      escrever(f'{Cor.VERDE}Recuperado com sucesso!{Cor.RESET}')
      aguardar()
      continue

    # Restaurar uma quantidade específica — fluxo antigo, pra quem quiser
    # economizar cobres curando só uma parte.
    opcoes_recurso = [f'{Cor.VERMELHO}Vida{Cor.RESET}', f'{Cor.AZUL}Mana{Cor.RESET}', 'Voltar']
    escolha_recurso = ler_acao('Restaurar quanto de qual recurso?', opcoes_recurso)
    if escolha_recurso is None or escolha_recurso == 2:
      continue

    recurso = 'vida' if escolha_recurso == 0 else 'mana'
    cor_recurso = Cor.VERMELHO if recurso == 'vida' else Cor.AZUL
    falta = falta_vida if recurso == 'vida' else falta_mana
    if falta <= 0:
      escrever(f'{cor_recurso}Sua {recurso} já está no máximo.{Cor.RESET}')
      aguardar()
      continue

    quantidade = pedir_numero(f'Quanto de {recurso} deseja restaurar (máx {falta})? -->',
                               minimo=1, maximo=falta, entrada=entrada_texto, saida=escrever)
    custo = _custo_cura(quantidade)
    if not perguntar_sim_nao(f'Isso vai custar {custo} cobres. Confirmar?'):
      continue
    if not _restaurar_recurso(personagem, escrever, recurso, quantidade):
      aguardar()
      continue
    escrever(f'{Cor.VERDE}{recurso.capitalize()} restaurada com sucesso!{Cor.RESET}')
    aguardar()


def _max_slots_habilidade(personagem):
  return 3 + personagem.slots_habilidade_comprados


def _comprar_slot_habilidade(personagem, escrever, aguardar):
  if personagem.slots_habilidade_comprados >= len(CUSTOS_SLOT_HABILIDADE):
    escrever(f'{Cor.CIANO}Você já tem o máximo de slots de habilidade.{Cor.RESET}')
    aguardar()
    return
  custo, campo_moeda = CUSTOS_SLOT_HABILIDADE[personagem.slots_habilidade_comprados]
  saldo = getattr(personagem, campo_moeda)
  if saldo < custo:
    escrever(f'{Cor.VERMELHO}Você não tem {custo} {_NOME_MOEDA[campo_moeda]} suficientes.{Cor.RESET}')
    aguardar()
    return
  setattr(personagem, campo_moeda, saldo - custo)
  personagem.slots_habilidade_comprados += 1
  escrever(f'{Cor.VERDE}Novo slot de habilidade desbloqueado! Total: '
           f'{_max_slots_habilidade(personagem)}.{Cor.RESET}')
  aguardar()


def tela_equipar_habilidades(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  indice = 0
  while True:
    max_slots = _max_slots_habilidade(personagem)
    tem_slot_vazio = len(personagem.habilidades_equipadas) < max_slots

    opcoes = [f'Slot {i + 1}: {Cor.BRANCO}{nome}{Cor.RESET} (equipada)'
              for i, nome in enumerate(personagem.habilidades_equipadas)]
    disponiveis = [nome for nome in personagem.habilidades_aprendidas
                   if nome not in personagem.habilidades_equipadas]
    total_slots_ocupados = len(opcoes)
    for nome in disponiveis:
      h = HABILIDADES[nome]
      efeito = f' | Efeito: {h.efeito}' if h.efeito else ''
      verbo = 'Equipar' if tem_slot_vazio else 'Trocar por'
      opcoes.append(f'{verbo}: {Cor.BRANCO}{nome}{Cor.RESET} '
                     f'({Cor.AZUL}{h.mana} mana{Cor.RESET}, {Cor.VERMELHO}{h.dano_base} dano base{Cor.RESET}'
                     f'{efeito})')

    indice_comprar_slot = None
    if personagem.slots_habilidade_comprados < len(CUSTOS_SLOT_HABILIDADE):
      custo, campo_moeda = CUSTOS_SLOT_HABILIDADE[personagem.slots_habilidade_comprados]
      indice_comprar_slot = len(opcoes)
      opcoes.append(f'Comprar slot de habilidade extra — {custo} {_NOME_MOEDA[campo_moeda]}')

    titulo = f'{_titulo(personagem, "Habilidades equipadas")} ({total_slots_ocupados}/{max_slots} slots)'
    escolha = ler_acao(titulo, opcoes, indice_inicial=indice)
    if escolha is None or escolha < total_slots_ocupados:
      return
    indice = escolha

    if indice_comprar_slot is not None and escolha == indice_comprar_slot:
      _comprar_slot_habilidade(personagem, escrever, aguardar)
      continue

    nome_nova = disponiveis[escolha - total_slots_ocupados]
    if tem_slot_vazio:
      personagem.habilidades_equipadas.append(nome_nova)
      escrever(f'{Cor.VERDE}Equipou {nome_nova}.{Cor.RESET}')
      aguardar()
      continue

    escolha_slot = ler_acao('Qual slot substituir?', personagem.habilidades_equipadas)
    if escolha_slot is None:
      continue
    antiga = personagem.habilidades_equipadas[escolha_slot]
    personagem.habilidades_equipadas[escolha_slot] = nome_nova
    escrever(f'{Cor.VERDE}Trocou {antiga} por {nome_nova}.{Cor.RESET}')
    aguardar()


def tela_status(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  indice = 0
  while True:
    vida_max = equipamento.vida_maxima_efetiva(personagem)
    mana_max = equipamento.mana_maxima_efetiva(personagem)
    critico = min(CHANCE_CRITICO_MAXIMA, batalha.chance_de_critico_base(personagem))
    linhas = [
      f'{personagem.raca} {personagem.classe} — Nv.{personagem.nivel} '
      f'(Exp {personagem.exp}/{personagem.exp_para_subir})',
      f'Vida:      {Cor.VERMELHO}{personagem.vida}/{vida_max}{Cor.RESET}',
      f'Mana:      {Cor.AZUL}{personagem.mana}/{mana_max}{Cor.RESET}',
      f'Poder:     {personagem.poder}',
      f'Esquiva:   {personagem.esquiva}%',
      f'Sorte:     {personagem.sorte}',
      f'Crítico:   {Cor.AMARELO}{critico}%{Cor.RESET}',
      f'Fome:      {personagem.fome}/{FOME_MAXIMA}',
      f'Postura:   {personagem.postura}',
    ]
    quadro = _desenhar_quadro(f'STATUS DE {personagem.nome}', linhas)
    titulo = (f'{quadro}\n\n'
              f'{Cor.BRANCO}Pontos de status disponíveis: {personagem.pontos_status}{Cor.RESET}')
    opcoes = ['+5 Vida máxima', '+5 Mana máxima', '+1 Poder', '+1 Sorte (crítico)', 'Equipar habilidades']
    escolha = ler_acao(titulo, opcoes, indice_inicial=indice)
    if escolha is None:
      return
    indice = escolha
    if escolha in (0, 1, 2, 3):
      if personagem.pontos_status < 1:
        escrever(f'{Cor.VERMELHO}Você não tem pontos de status disponíveis.{Cor.RESET}')
        aguardar()
        continue
      personagem.pontos_status -= 1
      if escolha == 0:
        personagem.vida_maxima += 5
        personagem.vida += 5
      elif escolha == 1:
        personagem.mana_maxima += 5
        personagem.mana += 5
      elif escolha == 2:
        personagem.poder += 1
      elif escolha == 3:
        personagem.sorte += 1
    elif escolha == 4:
      tela_equipar_habilidades(personagem, escrever, ler_acao, aguardar)


_NOME_MOEDA = {'moeda_cobre': 'cobres', 'moeda_prata': 'pratas', 'moeda_ouro': 'ouros'}


def _descricao_arma(nome):
  arma = ARMAS.get(nome) or next((a for a in ARMAS_LENDARIAS.values() if a.nome == nome), None)
  return f'{arma.bonus_poder_percentual}% poder, {arma.elemento}' if arma else ''


def _descricao_armadura(nome):
  armadura = ARMADURAS.get(nome) or ARMADURAS_UNICAS.get(nome)
  return armadura.descricao if armadura else ''


def _descricao_acessorio(nome):
  acessorio = ACESSORIOS.get(nome) or ACESSORIOS_UNICOS_POR_NOME.get(nome)
  return acessorio.descricao if acessorio else ''


def _max_slots_acessorio(personagem):
  return 1 + personagem.slots_acessorio_comprados


def _comprar_slot_acessorio(personagem, escrever, aguardar):
  if personagem.slots_acessorio_comprados >= len(CUSTOS_SLOT_ACESSORIO):
    escrever(f'{Cor.CIANO}Você já tem o máximo de slots de acessório.{Cor.RESET}')
    aguardar()
    return
  custo, campo_moeda = CUSTOS_SLOT_ACESSORIO[personagem.slots_acessorio_comprados]
  saldo = getattr(personagem, campo_moeda)
  if saldo < custo:
    escrever(f'{Cor.VERMELHO}Você não tem {custo} {_NOME_MOEDA[campo_moeda]} suficientes.{Cor.RESET}')
    aguardar()
    return
  setattr(personagem, campo_moeda, saldo - custo)
  personagem.slots_acessorio_comprados += 1
  escrever(f'{Cor.VERDE}Novo slot de acessório desbloqueado! Total: '
           f'{_max_slots_acessorio(personagem)}.{Cor.RESET}')
  aguardar()


def _quadro_equipamento(personagem, arma, armadura, acessorios, max_slots):
  """Substitui o antigo bloco de texto solto por um quadro ASCII, no mesmo
  molde do `STATUS DE ...` — a tela de Personagem tende a acumular muito
  acessório/arma/armadura guardado ao longo do jogo e virava só um monte de
  texto corrido."""
  linhas = [
    f'Arma:      {Cor.BRANCO}{arma.nome}{Cor.RESET} '
    f'({arma.bonus_poder_percentual}% poder, {arma.elemento})',
    f'Armadura:  {Cor.BRANCO}{armadura.nome if armadura else "Nenhuma"}{Cor.RESET}'
    + (f' ({armadura.descricao})' if armadura else ''),
    '',
    f'Acessórios ({len(acessorios)}/{max_slots}):',
  ]
  linhas += ([f'  - {a.nome}: {a.descricao}' for a in acessorios] if acessorios
             else ['  Nenhum equipado'])
  if personagem.itens_especiais:
    linhas.append('')
    linhas.append(f'Itens especiais: {Cor.CIANO}{", ".join(personagem.itens_especiais)}{Cor.RESET}')
  return _desenhar_quadro(f'EQUIPAMENTO DE {personagem.nome.upper()}', linhas, largura=90)


def tela_personagem(personagem, escrever=print, ler_acao=None, aguardar=None):
  """A lista de ações usa `secoes` (cabeçalhos visuais, sem virar sub-tela —
  ver `_opcoes_e_secoes_vila` em jogo.py pra mais contexto) pra separar
  arma/armadura/equipar acessório/desequipar acessório, que antes viravam
  uma lista só cada vez mais longa e difícil de escanear."""
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  indice = 0
  while True:
    arma = equipamento.resolver_arma(personagem)
    armadura = equipamento.resolver_armadura(personagem)
    acessorios = equipamento.resolver_acessorios(personagem)
    max_slots = _max_slots_acessorio(personagem)

    quadro = _quadro_equipamento(personagem, arma, armadura, acessorios, max_slots)
    titulo = f'{equipamento.resumo_status(personagem)}\n\n{quadro}'

    total_armas = len(personagem.equipamentos_guardados)
    total_armaduras = len(personagem.armaduras_guardadas)
    total_guardados_acessorio = len(personagem.acessorios_guardados)

    opcoes = []
    secoes = {}
    if personagem.equipamentos_guardados:
      secoes[len(opcoes)] = 'ARMAS'
      opcoes += [f'Equipar: {n} ({_descricao_arma(n)})' for n in personagem.equipamentos_guardados]
    if personagem.armaduras_guardadas:
      secoes[len(opcoes)] = 'ARMADURAS'
      opcoes += [f'Equipar: {n} ({_descricao_armadura(n)})' for n in personagem.armaduras_guardadas]
    if personagem.acessorios_guardados:
      secoes[len(opcoes)] = 'ACESSÓRIOS — equipar'
      opcoes += [f'Equipar: {n} ({_descricao_acessorio(n)})' for n in personagem.acessorios_guardados]
    if personagem.acessorios_equipados:
      secoes[len(opcoes)] = 'ACESSÓRIOS — desequipar'
      opcoes += [f'Desequipar: {n}' for n in personagem.acessorios_equipados]

    indice_comprar_slot = None
    if personagem.slots_acessorio_comprados < len(CUSTOS_SLOT_ACESSORIO):
      custo, campo_moeda = CUSTOS_SLOT_ACESSORIO[personagem.slots_acessorio_comprados]
      secoes[len(opcoes)] = 'LOJA'
      indice_comprar_slot = len(opcoes)
      opcoes.append(f'Comprar slot de acessório extra — {custo} {_NOME_MOEDA[campo_moeda]}')

    if not opcoes:
      # Antes isso só mostrava um erro e saía, sem nunca exibir o `titulo`
      # (que tem o equipamento atual) — parecia que o equipar tinha falhado,
      # mesmo quando tinha funcionado normalmente.
      titulo_vazio = (f'{titulo}\n\n'
                      f'{Cor.CIANO}Nada guardado pra trocar agora. Compre mais na loja.{Cor.RESET}')
      ler_acao(titulo_vazio, ['Voltar'], com_voltar=False)
      return

    escolha = ler_acao(titulo, opcoes, indice_inicial=indice, secoes=secoes)
    if escolha is None:
      return
    indice = escolha

    if escolha < total_armas:
      novo = personagem.equipamentos_guardados.pop(escolha)
      antigo = personagem.arma_equipada
      personagem.arma_equipada = novo
      if antigo:
        personagem.equipamentos_guardados.append(antigo)
    elif escolha < total_armas + total_armaduras:
      novo = personagem.armaduras_guardadas.pop(escolha - total_armas)
      antigo = personagem.armadura_equipada
      personagem.armadura_equipada = novo
      if antigo:
        personagem.armaduras_guardadas.append(antigo)
    elif escolha < total_armas + total_armaduras + total_guardados_acessorio:
      indice_guardado = escolha - total_armas - total_armaduras
      novo = personagem.acessorios_guardados[indice_guardado]
      if len(personagem.acessorios_equipados) < max_slots:
        personagem.acessorios_guardados.pop(indice_guardado)
        personagem.acessorios_equipados.append(novo)
      else:
        escolha_slot = ler_acao('Todos os slots de acessório estão ocupados. Qual remover?',
                                 personagem.acessorios_equipados)
        if escolha_slot is None:
          continue
        personagem.acessorios_guardados.pop(indice_guardado)
        antigo = personagem.acessorios_equipados.pop(escolha_slot)
        personagem.acessorios_equipados.append(novo)
        personagem.acessorios_guardados.append(antigo)
    elif indice_comprar_slot is not None and escolha == indice_comprar_slot:
      _comprar_slot_acessorio(personagem, escrever, aguardar)
      continue
    else:
      indice_equipado = (escolha - total_armas - total_armaduras - total_guardados_acessorio)
      removido = personagem.acessorios_equipados.pop(indice_equipado)
      personagem.acessorios_guardados.append(removido)
      escrever(f'{Cor.AMARELO}{removido} desequipado.{Cor.RESET}')
      aguardar()
      continue
    escrever(f'{Cor.VERDE}Equipado com sucesso!{Cor.RESET}')
    aguardar()


_LARGURA_QUADRO = 58


def _linha_quadro(texto, largura=_LARGURA_QUADRO):
  return f'|{ljust_visivel(" " + texto, largura - 2)}|'


def _desenhar_quadro(titulo, linhas, largura=_LARGURA_QUADRO):
  borda = '+' + '-' * (largura - 2) + '+'
  corpo = [borda, _linha_quadro(f'{Cor.BRANCO}{titulo}{Cor.RESET}', largura), borda]
  for linha in linhas:
    corpo.append(_linha_quadro(linha, largura))
  corpo.append(borda)
  return '\n'.join(corpo)


def tela_guia_elemental(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  ciclo = ' -> '.join(CICLO_ELEMENTAL + [CICLO_ELEMENTAL[0]])
  linhas = [
    'Fraqueza/resistência explícita de um monstro sempre valem mais que a',
    'roda genérica abaixo (ver a descrição de cada monstro em batalha):',
    f'  Fraqueza explícita: dano x{MULTIPLICADOR_FRAQUEZA_ELEMENTAL}',
    f'  Resistência explícita: dano x{MULTIPLICADOR_RESISTENCIA_ELEMENTAL}',
    '',
    'Sem fraqueza/resistência explícita, cada elemento é forte contra o',
    'próximo desta roda, e fraco contra o anterior:',
    f'  {ciclo}',
    f'  Vantagem da roda: dano x{MULTIPLICADOR_FRAQUEZA_CICLO}',
    f'  Desvantagem da roda: dano x{MULTIPLICADOR_RESISTENCIA_CICLO}',
  ]
  quadro = _desenhar_quadro('Guia Elemental', linhas, largura=72)
  ler_acao(quadro, ['Voltar'], com_voltar=False)


def _texto_tutorial_classes():
  return '\n'.join([
    f'{Cor.BRANCO}CAVALEIRO{Cor.RESET}',
    'Dano físico e mais vida, a classe mais resistente. Recurso próprio:',
    f'{Cor.AMARELO}Fúria{Cor.RESET} — começa em 0, PERSISTE entre batalhas (não zera ao',
    f'vencer/fugir). Ganha {FURIA_GANHA_AO_ATACAR} ao acertar um ataque e '
    f'{FURIA_GANHA_AO_LEVAR_DANO} ao levar dano.',
    'Habilidades marcadas com custo em Fúria gastam Fúria em vez de mana —',
    'guardar Fúria pra soltar o golpe mais forte no momento certo é a',
    'principal decisão tática da classe.',
    '',
    f'{Cor.BRANCO}ARQUEIRO{Cor.RESET}',
    'Ataques à distância com grande versatilidade elemental. Recurso próprio:',
    f'{Cor.AMARELO}Foco{Cor.RESET} — também persiste entre batalhas. Ganha '
    f'{FOCO_GANHO_POR_ATAQUE} ao acertar um',
    f'ataque, +{FOCO_GANHO_POR_CRITICO_EXTRA} extra se for crítico. Gasto em '
    'habilidades de custo em Foco.',
    'Pode trocar o elemento da própria flecha a qualquer momento em batalha',
    '(ação de graça, não gasta o turno) — ciclando pelos elementos do Guia',
    'Elemental, pra sempre acertar a fraqueza do inimigo.',
    f'Também tem acesso a "Marcar Alvo": aplica o efeito {Cor.AMARELO}Marcado{Cor.RESET}, que',
    f'aumenta em {MARCADO_BONUS_DANO_PERCENTUAL_PADRAO}% todo dano que o alvo recebe '
    '(de qualquer fonte) enquanto durar.',
    '',
    f'{Cor.BRANCO}MAGO{Cor.RESET}',
    'Dano mágico elemental puro, o mais frágil fisicamente. Recurso próprio:',
    f'{Cor.AMARELO}Ressonância Arcana{Cor.RESET} — ao contrário de Fúria/Foco, ZERA a cada',
    'batalha nova. Conjurar um elemento DIFERENTE do último aumenta uma',
    f'carga (até {RESSONANCIA_ARCANA_MAXIMA}, cada carga dá +'
    f'{RESSONANCIA_ARCANA_BONUS_POR_STACK}% de dano); repetir o mesmo',
    'elemento duas vezes seguidas ZERA todo o acúmulo. Ataques físicos não',
    'contam pra Ressonância. Recompensa alternar entre os elementos em vez',
    'de bater sempre com o mesmo golpe.',
  ])


def _texto_tutorial_especializacoes():
  linhas = [f'Escolhida a partir do nível {NIVEL_MINIMO_ESPECIALIZACAO} (uma vez, sem volta),',
            'cada especialização dá uma passiva permanente e uma habilidade exclusiva:', '']
  for classe, nomes in ESPECIALIZACOES_POR_CLASSE.items():
    linhas.append(f'{Cor.BRANCO}{classe}{Cor.RESET}')
    for nome in nomes:
      e = ESPECIALIZACOES[nome]
      linhas.append(f'  {Cor.AMARELO}{e.nome}{Cor.RESET} — {e.descricao} '
                     f'(habilidade nova: {e.habilidade_nova})')
    linhas.append('')
  return '\n'.join(linhas).rstrip()


def _texto_tutorial_recursos_e_postura():
  return '\n'.join([
    f'{Cor.BRANCO}POSTURA{Cor.RESET} (todas as classes, troca de graça, não gasta o turno)',
    f'  Ofensiva: {Cor.VERMELHO}+{BONUS_POSTURA_OFENSIVA_DANO}%{Cor.RESET} de dano causado, mas '
    f'{Cor.VERMELHO}+{BONUS_POSTURA_OFENSIVA_DANO_RECEBIDO}%{Cor.RESET} de dano recebido.',
    f'  Defensiva: {BONUS_POSTURA_DEFENSIVA_DANO}% de dano causado, mas '
    f'{Cor.VERDE}-{BONUS_POSTURA_DEFENSIVA_REDUCAO}%{Cor.RESET} de dano recebido.',
    '',
    f'{Cor.BRANCO}ATORDOAMENTO{Cor.RESET}',
    'Acertar a fraqueza elemental de um monstro acumula uma barra oculta',
    f'(+{ATORDOAMENTO_GANHO_POR_ACERTO_FRACO} por acerto). Ao encher '
    f'({ATORDOAMENTO_LIMIAR}), o monstro fica Atordoado e',
    'perde a ação seguinte — mais um motivo pra explorar fraquezas.',
    '',
    f'{Cor.BRANCO}ITENS EM BATALHA{Cor.RESET}',
    'Só é permitido usar 1 item por turno — mas usar item NÃO gasta o',
    'turno (você ainda pode agir normalmente depois).',
    '',
    f'{Cor.BRANCO}GRUPOS DE MONSTROS E ÁREA{Cor.RESET}',
    f'1 em cada {CHANCE_GRUPO_MONSTROS} encontros com monstros comuns vira um grupo de',
    '2-3 monstros de uma vez (chefes nunca vêm em grupo). Habilidades do',
    'tipo "ataque em área" acertam todos os monstros vivos de uma só vez.',
  ])


def _texto_tutorial_efeitos():
  return '\n'.join([
    f'{Cor.VERMELHO}Queimadura / Sangramento{Cor.RESET} — 15 de dano por turno.',
    f'{Cor.VERMELHO}Veneno{Cor.RESET} — 12 de dano por turno.',
    f'{Cor.VERDE}Regeneração{Cor.RESET} — cura 8% da vida máxima por turno.',
    f'{Cor.AMARELO}Paralisia / Atordoado{Cor.RESET} — impede agir no turno (a origem muda: '
    'Paralisia vem de',
    '  habilidade/ataque, Atordoado vem da barra de acúmulo na fraqueza',
    '  elemental — mas os dois têm o mesmo efeito de perder a vez).',
    f'{Cor.AMARELO}Fraqueza{Cor.RESET} — reduz o % de bônus de dano de quem está com o efeito.',
    f'{Cor.AMARELO}Vulnerabilidade / Marcado{Cor.RESET} — aumenta o % de dano recebido por quem',
    '  está com o efeito (Marcado é a versão do Arqueiro, mesma mecânica).',
    '',
    f'{Cor.CIANO}Detonar{Cor.RESET}: um ataque do elemento Físico (inclusive a flecha do',
    'Arqueiro trocada pra Físico) detona qualquer dano-por-turno ativo no',
    'alvo (Queimadura/Sangramento/Veneno), causando de uma vez todo o dano',
    'restante que ainda faltava.',
  ])


def _texto_tutorial_canalizacao():
  return '\n'.join([
    'Algumas habilidades são marcadas como Canalizáveis. Ao usá-las, você',
    'pode escolher canalizar: um mini-jogo de memória mostra uma sequência',
    f'de {SIMBOLOS_MINIGAME_CANALIZACAO} letras por um instante, e depois pede pra digitar de volta.',
    'Quanto mais letras você acertar na ordem certa, maior o bônus de dano',
    f'aplicado só naquele golpe — até +{BONUS_CANALIZACAO_MAXIMO_PERCENTUAL}% com acerto total.',
    'Errar tudo não penaliza; só não dá bônus nenhum.',
  ])


_TOPICOS_TUTORIAL = [
  ('Classes', _texto_tutorial_classes),
  ('Especializações', _texto_tutorial_especializacoes),
  ('Recursos e Postura', _texto_tutorial_recursos_e_postura),
  ('Efeitos de Status', _texto_tutorial_efeitos),
  ('Habilidades Canalizáveis', _texto_tutorial_canalizacao),
]


def tela_tutorial(personagem, escrever=print, ler_acao=None, aguardar=None):
  """Texto fixo e igual pra qualquer classe/personagem — o jogador pediu um
  lugar único com a explicação de tudo (elementos, Fúria, efeitos, classes,
  especializações etc.) em vez de ter que descobrir jogando."""
  ler_acao = ler_acao or menu_padrao
  indice = 0
  while True:
    opcoes = [titulo for titulo, _texto in _TOPICOS_TUTORIAL] + ['Guia Elemental', 'Voltar']
    escolha = ler_acao(_titulo(personagem, 'Tutorial'), opcoes, indice_inicial=indice)
    if escolha is None or escolha == len(opcoes) - 1:
      return
    indice = escolha
    if escolha == len(_TOPICOS_TUTORIAL):
      tela_guia_elemental(personagem, escrever, ler_acao, aguardar)
      continue
    _titulo_topico, gerar_texto = _TOPICOS_TUTORIAL[escolha]
    ler_acao(gerar_texto(), ['Voltar'], com_voltar=False)


def _resumo_missoes_ativas(personagem):
  if not personagem.missoes_ativas:
    return f'  {Cor.CINZA}Nenhuma missão equipada.{Cor.RESET}'
  linhas = []
  for missao in personagem.missoes_ativas:
    dungeon_nome = DUNGEONS[missao['dungeon_id']].nome
    linhas.append(f'  {Cor.BRANCO}{missao["monstro"]}{Cor.RESET} '
                   f'({missao["quantidade_atual"]}/{missao["quantidade_alvo"]}) '
                   f'— {dungeon_nome}, Andar {missao["andar"]}')
  return '\n'.join(linhas)


def tela_guilda(personagem, escrever=print, ler_acao=None, aguardar=None, _quadros_cache={}):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  indice = 0
  while True:
    dungeons_disponiveis = ['habusken']
    if personagem.torre_arcana_liberada:
      dungeons_disponiveis.append('torre_arcana')
    if personagem.abismo_submerso_liberado:
      dungeons_disponiveis.append('abismo_submerso')
    if personagem.cratera_vhalos_liberado:
      dungeons_disponiveis.append('cratera_vhalos')

    _, nome_tier = economia.tier_reputacao(personagem.reputacao_guilda)
    titulo = (f'{equipamento.resumo_status(personagem)}\n\n{Cor.ROSA}Guilda de Aventureiros{Cor.RESET}\n'
              f'Reputação: {personagem.reputacao_guilda} ({Cor.AMARELO}{nome_tier}{Cor.RESET})\n\n'
              f'Missões equipadas ({len(personagem.missoes_ativas)}/{MAX_MISSOES_ATIVAS}):\n'
              f'{_resumo_missoes_ativas(personagem)}\n\n'
              f'Escolha o quadro de missões de qual dungeon:')
    opcoes = [DUNGEONS[d].nome for d in dungeons_disponiveis]
    escolha = ler_acao(titulo, opcoes, indice_inicial=indice)
    if escolha is None:
      return
    indice = escolha
    _tela_quadro_andares(personagem, dungeons_disponiveis[escolha], escrever, ler_acao, aguardar,
                          _quadros_cache)


def _tela_quadro_andares(personagem, dungeon_id, escrever, ler_acao, aguardar, quadros_cache):
  dungeon = DUNGEONS[dungeon_id]
  indice = 0
  while True:
    maior = max(personagem.maior_andar_visitado.get(dungeon_id, 1),
                personagem.andar_atual.get(dungeon_id, 1))
    opcoes = [f'Andar {n} — {dungeon.andares[n - 1].nome}' for n in range(1, maior + 1)]
    titulo = (f'{Cor.ROSA}Guilda — {dungeon.nome}{Cor.RESET}\n\n'
              f'Só existe quadro de missões dos andares que você já pisou.\n'
              f'Escolha um andar:')
    escolha = ler_acao(titulo, opcoes, indice_inicial=indice)
    if escolha is None:
      return
    indice = escolha
    _tela_quadro_missoes(personagem, dungeon_id, escolha + 1, escrever, ler_acao, aguardar, quadros_cache)


def _tela_quadro_missoes(personagem, dungeon_id, andar_numero, escrever, ler_acao, aguardar, quadros_cache):
  chave = (personagem.nome, dungeon_id, andar_numero)
  if chave not in quadros_cache:
    quadros_cache[chave] = economia.gerar_missoes_do_andar(personagem, dungeon_id, andar_numero)

  cursor = 0
  while True:
    quadro = quadros_cache[chave]
    linhas_quadro = []
    for missao in quadro:
      marca = f'{Cor.VERDE}[x]{Cor.RESET}' if economia.missao_equipada(personagem, missao) else '[ ]'
      linhas_quadro.append(f'{marca} Matar {missao["quantidade_alvo"]}x {missao["monstro"]} — '
                            f'{missao["recompensa_exp"]} exp, {missao["recompensa_moedas"]} cobres')
    quadro_ascii = _desenhar_quadro(
        f'Andar {andar_numero} — {DUNGEONS[dungeon_id].nome}', linhas_quadro)

    titulo = (f'{equipamento.resumo_status(personagem)}\n\n{quadro_ascii}\n\n'
              f'Missões equipadas ({len(personagem.missoes_ativas)}/{MAX_MISSOES_ATIVAS}):\n'
              f'{_resumo_missoes_ativas(personagem)}')

    opcoes = []
    for indice, missao in enumerate(quadro):
      equipada = economia.missao_equipada(personagem, missao)
      opcoes.append(f'{"Desequipar" if equipada else "Equipar"} missão {indice + 1}')
    opcoes.append(f'Renovar quadro ({CUSTO_RENOVAR_QUADRO} cobres)')

    escolha = ler_acao(titulo, opcoes, indice_inicial=cursor)
    if escolha is None:
      return
    cursor = escolha

    if escolha < len(quadro):
      missao = quadro[escolha]
      if economia.missao_equipada(personagem, missao):
        indice_ativo = next(i for i, m in enumerate(personagem.missoes_ativas)
                             if m['dungeon_id'] == missao['dungeon_id'] and m['andar'] == missao['andar']
                             and m['quadro_indice'] == missao['quadro_indice'])
        economia.abandonar_missao(personagem, indice_ativo)
        escrever(f'{Cor.AMARELO}Missão desequipada.{Cor.RESET}')
      elif economia.aceitar_missao(personagem, missao):
        escrever(f'{Cor.VERDE}Missão equipada!{Cor.RESET}')
      else:
        escrever(f'{Cor.VERMELHO}Você já tem {MAX_MISSOES_ATIVAS} missões equipadas. '
                 f'Desequipe uma primeiro.{Cor.RESET}')
      aguardar()
    else:
      if personagem.moeda_cobre < CUSTO_RENOVAR_QUADRO:
        escrever(f'{Cor.VERMELHO}Você não tem {CUSTO_RENOVAR_QUADRO} cobres.{Cor.RESET}')
        aguardar()
        continue
      personagem.moeda_cobre -= CUSTO_RENOVAR_QUADRO
      quadros_cache[chave] = economia.gerar_missoes_do_andar(personagem, dungeon_id, andar_numero)
      escrever(f'{Cor.VERDE}Quadro renovado.{Cor.RESET}')
      aguardar()


def tela_desbloquear_habilidades(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  indice = 0
  while True:
    candidatas = [nome for nome in HABILIDADES_DESBLOQUEAVEIS.get(personagem.classe, [])
                  if nome not in personagem.habilidades_aprendidas]
    if not candidatas:
      escrever(f'{Cor.CIANO}Você já aprendeu todas as habilidades disponíveis para sua classe.{Cor.RESET}')
      aguardar()
      return
    opcoes = [f'{Cor.BRANCO}{nome}{Cor.RESET} — nível {HABILIDADES[nome].nivel_minimo}, '
              f'{HABILIDADES[nome].preco} cobres' for nome in candidatas]
    escolha = ler_acao(_titulo(personagem, 'Habilidades para desbloquear'), opcoes, indice_inicial=indice)
    if escolha is None:
      return
    indice = escolha
    nome = candidatas[escolha]
    habilidade = HABILIDADES[nome]
    if personagem.nivel < habilidade.nivel_minimo:
      escrever(f'{Cor.VERMELHO}Você não tem nível suficiente.{Cor.RESET}')
      aguardar()
      continue
    if personagem.moeda_cobre < habilidade.preco:
      escrever(f'{Cor.VERMELHO}Você não tem cobres suficientes.{Cor.RESET}')
      aguardar()
      continue
    personagem.moeda_cobre -= habilidade.preco
    personagem.habilidades_aprendidas.append(nome)
    escrever(f'{Cor.VERDE}Você aprendeu {nome}! Equipe-a em Status -> Equipar Habilidades.{Cor.RESET}')
    aguardar()


def tela_especializacao(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  if personagem.especializacao:
    escrever(f'{Cor.CIANO}Você já é um(a) {personagem.especializacao}. A escolha é permanente.{Cor.RESET}')
    aguardar()
    return
  if personagem.nivel < NIVEL_MINIMO_ESPECIALIZACAO:
    escrever(f'{Cor.VERMELHO}Você precisa ser nível {NIVEL_MINIMO_ESPECIALIZACAO} para se '
             f'especializar.{Cor.RESET}')
    aguardar()
    return
  nomes = ESPECIALIZACOES_POR_CLASSE.get(personagem.classe, [])
  opcoes = [f'{Cor.BRANCO}{nome}{Cor.RESET} — {ESPECIALIZACOES[nome].descricao}' for nome in nomes]
  escolha = ler_acao(_titulo(personagem, 'Escolha sua especialização (permanente)'), opcoes)
  if escolha is None:
    return
  especializacao = ESPECIALIZACOES[nomes[escolha]]
  personagem.especializacao = especializacao.nome
  if especializacao.bonus_tipo == 'vida_maxima':
    personagem.vida_maxima = round(personagem.vida_maxima * (1 + especializacao.bonus_valor / 100))
    personagem.vida = personagem.vida_maxima
  elif especializacao.bonus_tipo == 'esquiva_flat':
    personagem.esquiva += especializacao.bonus_valor
  personagem.habilidades_aprendidas.append(especializacao.habilidade_nova)
  escrever(f'{Cor.VERDE}Você se tornou um(a) {especializacao.nome}! Aprendeu '
           f'{especializacao.habilidade_nova}.{Cor.RESET}')
  aguardar()


def tela_ferreiro(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  indice = 0
  while True:
    tem_arma = bool(personagem.arma_equipada)
    tem_armadura = bool(personagem.armadura_equipada)
    opcoes = []
    if tem_arma and personagem.encantamento_arma < ENCANTAMENTO_MAXIMO_ARMA:
      custo = ENCANTAMENTO_CUSTO_PRATA_BASE * (personagem.encantamento_arma // ENCANTAMENTO_INCREMENTO + 1)
      opcoes.append(f'Encantar arma (+{ENCANTAMENTO_INCREMENTO}%, atual +{personagem.encantamento_arma}%) '
                    f'— {custo} pratas + 1x {ENCANTAMENTO_MATERIAL}')
    if tem_armadura and personagem.encantamento_armadura < ENCANTAMENTO_MAXIMO_ARMADURA:
      custo = ENCANTAMENTO_CUSTO_PRATA_BASE * (personagem.encantamento_armadura // ENCANTAMENTO_INCREMENTO + 1)
      opcoes.append(f'Encantar armadura (+{ENCANTAMENTO_INCREMENTO}%, atual '
                    f'+{personagem.encantamento_armadura}%) — {custo} pratas + 1x {ENCANTAMENTO_MATERIAL}')
    if not opcoes:
      escrever(f'{Cor.CIANO}Nada para encantar agora (equipe uma arma/armadura, ou já está no '
               f'máximo).{Cor.RESET}')
      aguardar()
      return
    escolha = ler_acao(_titulo(personagem, 'Ferreiro — Encantamento'), opcoes, indice_inicial=indice)
    if escolha is None:
      return
    indice = escolha
    alvo_arma = tem_arma and personagem.encantamento_arma < ENCANTAMENTO_MAXIMO_ARMA and escolha == 0
    custo = (ENCANTAMENTO_CUSTO_PRATA_BASE
             * ((personagem.encantamento_arma if alvo_arma else personagem.encantamento_armadura)
                // ENCANTAMENTO_INCREMENTO + 1))
    if personagem.moeda_prata < custo:
      escrever(f'{Cor.VERMELHO}Você não tem pratas suficientes.{Cor.RESET}')
      aguardar()
      continue
    if not personagem.remover_material(ENCANTAMENTO_MATERIAL):
      escrever(f'{Cor.VERMELHO}Você não tem {ENCANTAMENTO_MATERIAL} suficiente.{Cor.RESET}')
      aguardar()
      continue
    personagem.moeda_prata -= custo
    if alvo_arma:
      personagem.encantamento_arma += ENCANTAMENTO_INCREMENTO
    else:
      personagem.encantamento_armadura += ENCANTAMENTO_INCREMENTO
    escrever(f'{Cor.VERDE}Encantamento aplicado com sucesso!{Cor.RESET}')
    aguardar()


def tela_estatisticas(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  titulo = (f'{Cor.BRANCO}Estatísticas de {personagem.nome}{Cor.RESET}\n\n'
            f'Nível: {personagem.nivel}\n'
            f'Especialização: {personagem.especializacao or "Nenhuma"}\n'
            f'Monstros derrotados: {personagem.monstros_derrotados}\n'
            f'Chefes derrotados: {len(personagem.chefes_derrotados)}\n'
            f'Missões completadas: {personagem.missoes_completadas}\n'
            f'Reputação com a guilda: {personagem.reputacao_guilda}\n'
            f'Moedas totais ganhas: {personagem.moedas_totais_ganhas}\n'
            f'Personagem criado em: {personagem.data_criacao}')
  ler_acao(titulo, ['Voltar'], com_voltar=False)


def tela_mapa_progresso(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  from ..dados.dungeons import DUNGEONS
  linhas = [f'{Cor.BRANCO}Mapa de progresso{Cor.RESET}']
  for dungeon_id, dungeon in DUNGEONS.items():
    andar_atual = personagem.andar_atual.get(dungeon_id, 1)
    linhas.append(f'\n{Cor.CIANO}{dungeon.nome}{Cor.RESET}')
    for andar in dungeon.andares:
      if andar.numero < andar_atual or andar.chefe in personagem.chefes_derrotados:
        status = f'{Cor.VERDE}concluído{Cor.RESET}'
      elif andar.numero == andar_atual:
        status = f'{Cor.AMARELO}em progresso{Cor.RESET}'
      else:
        status = f'{Cor.CINZA}bloqueado{Cor.RESET}'
      linhas.append(f'  Andar {andar.numero} — {andar.nome} ({andar.faixa_nivel}) — {status}')
  ler_acao('\n'.join(linhas), ['Voltar'], com_voltar=False)


def _verificar_novas_conquistas(personagem, escrever):
  """Conquista não tem sistema de eventos — é só um predicado sobre o estado
  atual, então a única hora sensata de checar se algo NOVO foi desbloqueado é
  quando o jogador abre o diário. `conquistas_desbloqueadas` garante que a
  recompensa só é concedida na primeira vez."""
  from ..dados.conquistas import CONQUISTAS
  novas = []
  for conquista in CONQUISTAS.values():
    if conquista.id in personagem.conquistas_desbloqueadas:
      continue
    if not conquista.verificar(personagem):
      continue
    personagem.conquistas_desbloqueadas.append(conquista.id)
    personagem.exp += conquista.recompensa_exp
    personagem.moeda_cobre += conquista.recompensa_moedas
    personagem.moedas_totais_ganhas += conquista.recompensa_moedas
    novas.append(conquista)
  for conquista in novas:
    escrever(f'{Cor.AMARELO}Conquista desbloqueada: {conquista.nome}! '
             f'(+{conquista.recompensa_exp} exp, +{conquista.recompensa_moedas} cobres){Cor.RESET}')
  return novas


def tela_diario_conquistas(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  from ..dados.conquistas import CONQUISTAS

  if _verificar_novas_conquistas(personagem, escrever):
    aguardar()

  linhas = [f'{Cor.BRANCO}Diário de Conquistas{Cor.RESET} '
            f'({len(personagem.conquistas_desbloqueadas)}/{len(CONQUISTAS)})\n']
  for conquista in CONQUISTAS.values():
    if conquista.id in personagem.conquistas_desbloqueadas:
      marca = f'{Cor.VERDE}[X]{Cor.RESET}'
    else:
      marca = f'{Cor.CINZA}[ ]{Cor.RESET}'
    linhas.append(f'{marca} {Cor.BRANCO}{conquista.nome}{Cor.RESET} — {conquista.descricao}')
  ler_acao('\n'.join(linhas), ['Voltar'], com_voltar=False)


def tela_bau(personagem, escrever=print, ler_acao=None, entrada_texto=input, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  indice = 0
  while True:
    titulo = (f'{equipamento.resumo_status(personagem)}\n\n'
              f'Cobres: {personagem.moeda_cobre}\n'
              f'Pratas: {personagem.moeda_prata}\n'
              f'Ouros: {personagem.moeda_ouro}')
    opcoes = ['Cobre -> Prata (1000:1)', 'Prata -> Cobre', 'Prata -> Ouro (1000:1)', 'Ouro -> Prata', 'Voltar']
    escolha = ler_acao(titulo, opcoes, indice_inicial=indice)
    if escolha is None or escolha == 4:
      return
    indice = escolha
    origem, destino = [('cobre', 'prata'), ('prata', 'cobre'), ('prata', 'ouro'), ('ouro', 'prata')][escolha]
    quantidade = pedir_numero(f'Quanto de {origem} deseja converter? -->',
                               minimo=1, entrada=entrada_texto, saida=escrever)
    sucesso, mensagem = economia.converter(personagem, origem, destino, quantidade)
    cor = Cor.VERDE if sucesso else Cor.VERMELHO
    escrever(f'{cor}{mensagem}{Cor.RESET}')
    aguardar()


def tela_mestre_habusken(personagem, escrever=print, ler_acao=None, entrada_texto=input,
                          esperar=None, aguardar=None, limpar=None):
  ler_acao = ler_acao or menu_padrao
  esperar = esperar or time.sleep
  aguardar = aguardar or aguardar_leitura
  limpar = limpar or limpar_tela
  if 'Slime Gigante' not in personagem.chefes_derrotados:
    escrever(f'{Cor.VERMELHO}O Mestre de Habusken não te reconhece como discípulo. '
              f'Derrote o chefe do Andar 1 primeiro.{Cor.RESET}')
    aguardar()
    return
  indice = 0
  while True:
    opcoes = [f'Treinar (50 cobres) — {personagem.treinamento_habusken}% concluído', 'Voltar']
    escolha = ler_acao(_titulo(personagem, 'Mestre de Habusken'), opcoes, indice_inicial=indice)
    if escolha is None or escolha == 1:
      return
    indice = escolha
    if personagem.moeda_cobre < 50:
      escrever(f'{Cor.VERMELHO}Você não tem 50 cobres.{Cor.RESET}')
      aguardar()
      continue
    personagem.moeda_cobre -= 50

    letras = [random.choice(string.ascii_uppercase) for _ in range(5)]
    limpar()
    escrever(f'{Cor.BRANCO}Decore a sequência de letras a seguir:{Cor.RESET}')
    for letra in letras:
      escrever(f'{Cor.AMARELO}{letra}{Cor.RESET}')
      esperar(1)
    esperar(3)
    limpar()
    resposta = entrada_texto('Digite as letras na ordem, separadas por espaço: -->')
    acertos = sum(1 for certa, digitada in zip(letras, resposta.upper().split()) if certa == digitada)
    personagem.treinamento_habusken = min(100, personagem.treinamento_habusken + acertos * 4)
    escrever(f'{Cor.VERDE}Você acertou {acertos} de {len(letras)} letras!{Cor.RESET}')
    if personagem.treinamento_habusken >= 100 and not personagem.eten:
      personagem.eten = True
      escrever(f'{Cor.VERDE}Você concluiu o treinamento! Aprendeu Etén: '
               f'+{BONUS_ETEN_PERCENTUAL}% de dano em todos os ataques.{Cor.RESET}')
    aguardar()


def tela_crafting(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  receitas = list(RECEITAS.values())
  indice = 0
  while True:
    opcoes = []
    for receita in receitas:
      requisitos = ', '.join(f'{qtd}x {nome}' for nome, qtd in receita.materiais_necessarios.items())
      opcoes.append(f'{Cor.BRANCO}{receita.nome}{Cor.RESET} (precisa: {requisitos})')
    escolha = ler_acao(_titulo(personagem, 'Bancada de Trabalho'), opcoes, indice_inicial=indice)
    if escolha is None:
      return
    indice = escolha
    sistema_crafting.craftar(personagem, receitas[escolha], escrever)
    aguardar()
