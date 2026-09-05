"""Todas as telas da Vila Habusken que não são a loja nem a dungeon."""

import random
import string
import time

from ..config import Cor
from ..dados.habilidades import HABILIDADES, HABILIDADES_DESBLOQUEAVEIS
from ..dados.receitas import RECEITAS
from ..entrada import aguardar_leitura
from ..entrada import menu as menu_padrao
from ..entrada import pedir_numero, perguntar_sim_nao
from . import crafting as sistema_crafting
from . import economia, equipamento, inventario


def tela_casa(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    opcoes = ['Descansar (recupera tudo, 1x por nível)', 'Comer', 'Voltar']
    escolha = ler_acao('Casa', opcoes)
    if escolha is None or escolha == 2:
      return
    if escolha == 0:
      if personagem.descansos_usados >= personagem.nivel:
        escrever(f'{Cor.VERMELHO}Você já descansou o máximo de vezes permitido neste nível.{Cor.RESET}')
        aguardar()
        continue
      personagem.descansos_usados += 1
      personagem.curar_totalmente()
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


def tela_curandeira(personagem, escrever=print, ler_acao=None, entrada_texto=input, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    opcoes = [f'Restaurar {Cor.VERMELHO}vida{Cor.RESET} (1 moeda a cada 5 de vida)',
              f'Restaurar {Cor.AZUL}mana{Cor.RESET} (1 moeda a cada 5 de mana)', 'Voltar']
    escolha = ler_acao('Curandeira', opcoes)
    if escolha is None or escolha == 2:
      return

    recurso = 'vida' if escolha == 0 else 'mana'
    cor_recurso = Cor.VERMELHO if recurso == 'vida' else Cor.AZUL
    if recurso == 'vida':
      maximo, atual = equipamento.vida_maxima_efetiva(personagem), personagem.vida
    else:
      maximo, atual = equipamento.mana_maxima_efetiva(personagem), personagem.mana
    falta = maximo - atual
    if falta <= 0:
      escrever(f'{cor_recurso}Sua {recurso} já está no máximo.{Cor.RESET}')
      aguardar()
      continue

    quantidade = pedir_numero(f'Quanto de {recurso} deseja restaurar (máx {falta})? -->',
                               minimo=1, maximo=falta, entrada=entrada_texto, saida=escrever)
    custo = max(1, quantidade // 5)
    if not perguntar_sim_nao(f'Isso vai custar {custo} moedas de cobre. Confirmar?'):
      continue
    if personagem.moeda_cobre < custo:
      escrever(f'{Cor.VERMELHO}Você não tem moedas de cobre suficientes.{Cor.RESET}')
      aguardar()
      continue

    personagem.moeda_cobre -= custo
    if recurso == 'vida':
      personagem.vida += quantidade
    else:
      personagem.mana += quantidade
    escrever(f'{Cor.VERDE}{recurso.capitalize()} restaurada com sucesso!{Cor.RESET}')
    aguardar()


def tela_equipar_habilidades(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    opcoes = [f'Slot {i + 1}: {Cor.BRANCO}{nome}{Cor.RESET} (equipada)'
              for i, nome in enumerate(personagem.habilidades_equipadas)]
    disponiveis = [nome for nome in personagem.habilidades_aprendidas
                   if nome not in personagem.habilidades_equipadas]
    for nome in disponiveis:
      h = HABILIDADES[nome]
      efeito = f' | Efeito: {h.efeito}' if h.efeito else ''
      opcoes.append(f'Trocar por: {Cor.BRANCO}{nome}{Cor.RESET} '
                     f'({Cor.AZUL}{h.mana} mana{Cor.RESET}, {Cor.VERMELHO}{h.dano_base} dano base{Cor.RESET}'
                     f'{efeito})')

    escolha = ler_acao('Habilidades equipadas', opcoes)
    if escolha is None or escolha < len(personagem.habilidades_equipadas):
      return

    nome_nova = disponiveis[escolha - len(personagem.habilidades_equipadas)]
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
  while True:
    vida_max = equipamento.vida_maxima_efetiva(personagem)
    mana_max = equipamento.mana_maxima_efetiva(personagem)
    titulo = (f'Nível {personagem.nivel} — Exp {personagem.exp}/{personagem.exp_para_subir}\n'
              f'{Cor.VERMELHO}Vida: {personagem.vida}/{vida_max}{Cor.RESET}   '
              f'{Cor.AZUL}Mana: {personagem.mana}/{mana_max}{Cor.RESET}\n'
              f'Poder: {personagem.poder}   Esquiva: {personagem.esquiva}%   Sorte: {personagem.sorte}\n'
              f'{Cor.BRANCO}Pontos de status disponíveis: {personagem.pontos_status}{Cor.RESET}')
    opcoes = ['+5 Vida máxima', '+5 Mana máxima', '+1 Poder', '+1 Sorte (crítico)', 'Equipar habilidades']
    escolha = ler_acao(titulo, opcoes)
    if escolha is None:
      return
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


def tela_personagem(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    arma = equipamento.resolver_arma(personagem)
    armadura = equipamento.resolver_armadura(personagem)
    acessorio = equipamento.resolver_acessorio(personagem)
    titulo = (f'Arma: {Cor.BRANCO}{arma.nome}{Cor.RESET} ({arma.bonus_poder_percentual}% poder)\n'
              f'Armadura: {Cor.BRANCO}{armadura.nome if armadura else "Nenhuma"}{Cor.RESET}\n'
              f'Acessório: {Cor.BRANCO}{acessorio.nome if acessorio else "Nenhum"}{Cor.RESET}')

    opcoes = ([f'Equipar arma: {n}' for n in personagem.equipamentos_guardados] +
              [f'Equipar armadura: {n}' for n in personagem.armaduras_guardadas] +
              [f'Equipar acessório: {n}' for n in personagem.acessorios_guardados])
    if not opcoes:
      escrever(f'{Cor.VERMELHO}Você não tem nada guardado para trocar. Compre na loja.{Cor.RESET}')
      aguardar()
      return

    escolha = ler_acao(titulo, opcoes)
    if escolha is None:
      return

    total_armas = len(personagem.equipamentos_guardados)
    total_armaduras = len(personagem.armaduras_guardadas)

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
    else:
      novo = personagem.acessorios_guardados.pop(escolha - total_armas - total_armaduras)
      antigo = personagem.acessorio_equipado
      personagem.acessorio_equipado = novo
      if antigo:
        personagem.acessorios_guardados.append(antigo)
    escrever(f'{Cor.VERDE}Equipado com sucesso!{Cor.RESET}')
    aguardar()


def tela_guilda(personagem, escrever=print, ler_acao=None, aguardar=None, _missoes_cache={}):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  if personagem.nome not in _missoes_cache:
    _missoes_cache[personagem.nome] = economia.gerar_missoes(personagem)
  while True:
    missoes = _missoes_cache[personagem.nome]
    opcoes = [f'Matar {m["quantidade"]}x {m["monstro"]} — {Cor.VERDE}{m["recompensa_exp"]} exp, '
              f'{m["recompensa_moedas"]} moedas{Cor.RESET}' for m in missoes]
    opcoes.append('Renovar missões (100 moedas)')
    if personagem.missao_monstro:
      opcoes.append(f'Abandonar missão atual ({personagem.missao_monstro})')

    titulo = f'{Cor.ROSA}Guilda{Cor.RESET}'
    if personagem.missao_monstro:
      titulo += (f'\nMissão ativa: matar {personagem.missao_monstro} '
                 f'({personagem.missao_quantidade_atual}/{personagem.missao_quantidade_alvo})')

    escolha = ler_acao(titulo, opcoes)
    if escolha is None:
      return
    if escolha < len(missoes):
      if personagem.missao_monstro:
        escrever(f'{Cor.VERMELHO}Você já está em uma missão. Abandone-a primeiro.{Cor.RESET}')
        aguardar()
        continue
      economia.aceitar_missao(personagem, missoes[escolha])
      escrever(f'{Cor.VERDE}Missão aceita!{Cor.RESET}')
      aguardar()
    elif escolha == len(missoes):
      if personagem.moeda_cobre < 100:
        escrever(f'{Cor.VERMELHO}Você não tem 100 moedas de cobre.{Cor.RESET}')
        aguardar()
        continue
      personagem.moeda_cobre -= 100
      _missoes_cache[personagem.nome] = economia.gerar_missoes(personagem)
      escrever(f'{Cor.VERDE}Missões renovadas.{Cor.RESET}')
      aguardar()
    else:
      economia.abandonar_missao(personagem)
      escrever(f'{Cor.AMARELO}Missão abandonada.{Cor.RESET}')
      aguardar()


def tela_desbloquear_habilidades(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    candidatas = [nome for nome in HABILIDADES_DESBLOQUEAVEIS.get(personagem.classe, [])
                  if nome not in personagem.habilidades_aprendidas]
    if not candidatas:
      escrever(f'{Cor.CIANO}Você já aprendeu todas as habilidades disponíveis para sua classe.{Cor.RESET}')
      aguardar()
      return
    opcoes = [f'{Cor.BRANCO}{nome}{Cor.RESET} — nível {HABILIDADES[nome].nivel_minimo}, '
              f'{HABILIDADES[nome].preco} moedas' for nome in candidatas]
    escolha = ler_acao('Habilidades para desbloquear', opcoes)
    if escolha is None:
      return
    nome = candidatas[escolha]
    habilidade = HABILIDADES[nome]
    if personagem.nivel < habilidade.nivel_minimo:
      escrever(f'{Cor.VERMELHO}Você não tem nível suficiente.{Cor.RESET}')
      aguardar()
      continue
    if personagem.moeda_cobre < habilidade.preco:
      escrever(f'{Cor.VERMELHO}Você não tem moedas de cobre suficientes.{Cor.RESET}')
      aguardar()
      continue
    personagem.moeda_cobre -= habilidade.preco
    personagem.habilidades_aprendidas.append(nome)
    escrever(f'{Cor.VERDE}Você aprendeu {nome}! Equipe-a em Status -> Equipar Habilidades.{Cor.RESET}')
    aguardar()


def tela_bau(personagem, escrever=print, ler_acao=None, entrada_texto=input, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    titulo = (f'Moedas de Cobre: {personagem.moeda_cobre}\n'
              f'Moedas de Prata: {personagem.moeda_prata}\n'
              f'Moedas de Ouro: {personagem.moeda_ouro}')
    opcoes = ['Cobre -> Prata (1000:1)', 'Prata -> Cobre', 'Prata -> Ouro (1000:1)', 'Ouro -> Prata', 'Voltar']
    escolha = ler_acao(titulo, opcoes)
    if escolha is None or escolha == 4:
      return
    origem, destino = [('cobre', 'prata'), ('prata', 'cobre'), ('prata', 'ouro'), ('ouro', 'prata')][escolha]
    quantidade = pedir_numero(f'Quanto de {origem} deseja converter? -->',
                               minimo=1, entrada=entrada_texto, saida=escrever)
    sucesso, mensagem = economia.converter(personagem, origem, destino, quantidade)
    cor = Cor.VERDE if sucesso else Cor.VERMELHO
    escrever(f'{cor}{mensagem}{Cor.RESET}')
    aguardar()


def tela_mestre_habusken(personagem, escrever=print, ler_acao=None, entrada_texto=input,
                          esperar=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  esperar = esperar or time.sleep
  aguardar = aguardar or aguardar_leitura
  if 'Slime Gigante' not in personagem.chefes_derrotados:
    escrever(f'{Cor.VERMELHO}O Mestre de Habusken não te reconhece como discípulo. '
              f'Derrote o chefe do Andar 1 primeiro.{Cor.RESET}')
    aguardar()
    return
  while True:
    opcoes = [f'Treinar (50 moedas) — {personagem.treinamento_habusken}% concluído', 'Voltar']
    escolha = ler_acao('Mestre de Habusken', opcoes)
    if escolha is None or escolha == 1:
      return
    if personagem.moeda_cobre < 50:
      escrever(f'{Cor.VERMELHO}Você não tem 50 moedas de cobre.{Cor.RESET}')
      aguardar()
      continue
    personagem.moeda_cobre -= 50

    letras = [random.choice(string.ascii_uppercase) for _ in range(5)]
    escrever(f'{Cor.BRANCO}Decore a sequência de letras a seguir:{Cor.RESET}')
    for letra in letras:
      escrever(f'{Cor.AMARELO}{letra}{Cor.RESET}')
      esperar(1)
    resposta = entrada_texto('Digite as letras na ordem, separadas por espaço: -->')
    acertos = sum(1 for certa, digitada in zip(letras, resposta.upper().split()) if certa == digitada)
    personagem.treinamento_habusken = min(100, personagem.treinamento_habusken + acertos * 4)
    escrever(f'{Cor.VERDE}Você acertou {acertos} de {len(letras)} letras!{Cor.RESET}')
    if personagem.treinamento_habusken >= 100 and not personagem.eten:
      personagem.eten = True
      escrever(f'{Cor.VERDE}Você concluiu o treinamento! Aprendeu Etén: '
               f'+30% de dano em todos os ataques.{Cor.RESET}')
    aguardar()


def tela_crafting(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  receitas = list(RECEITAS.values())
  while True:
    opcoes = []
    for receita in receitas:
      requisitos = ', '.join(f'{qtd}x {nome}' for nome, qtd in receita.materiais_necessarios.items())
      opcoes.append(f'{Cor.BRANCO}{receita.nome}{Cor.RESET} (precisa: {requisitos})')
    escolha = ler_acao('Bancada de Trabalho', opcoes)
    if escolha is None:
      return
    sistema_crafting.craftar(personagem, receitas[escolha], escrever)
    aguardar()
