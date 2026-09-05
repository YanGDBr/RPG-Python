"""Todas as telas da Vila Habusken que não são a loja nem a dungeon."""

import random
import string
import time

from ..dados.habilidades import HABILIDADES, HABILIDADES_DESBLOQUEAVEIS
from ..dados.receitas import RECEITAS
from ..entrada import menu as menu_padrao
from ..entrada import pedir_numero, perguntar_sim_nao
from . import crafting as sistema_crafting
from . import economia, equipamento, inventario


def tela_casa(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  while True:
    opcoes = ['Descansar (recupera tudo, 1x por nível)', 'Comer', 'Voltar']
    escolha = ler_acao('Casa', opcoes)
    if escolha is None or escolha == 2:
      return
    if escolha == 0:
      if personagem.descansos_usados >= personagem.nivel:
        escrever('Você já descansou o máximo de vezes permitido neste nível.')
        continue
      personagem.descansos_usados += 1
      personagem.curar_totalmente()
      escrever('Você descansou e se recuperou completamente!')
    elif escolha == 1:
      comidas_disponiveis = [nome for nome, qtd in personagem.comidas.items() if qtd > 0]
      if not comidas_disponiveis:
        escrever('Você não tem nenhuma comida.')
        continue
      escolha_comida = ler_acao('O que deseja comer?', comidas_disponiveis)
      if escolha_comida is not None:
        inventario.comer(personagem, comidas_disponiveis[escolha_comida], escrever)


def tela_curandeira(personagem, escrever=print, ler_acao=None, entrada_texto=input):
  ler_acao = ler_acao or menu_padrao
  while True:
    opcoes = ['Restaurar vida (1 moeda a cada 5 de vida)',
              'Restaurar mana (1 moeda a cada 5 de mana)', 'Voltar']
    escolha = ler_acao('Curandeira', opcoes)
    if escolha is None or escolha == 2:
      return

    recurso = 'vida' if escolha == 0 else 'mana'
    if recurso == 'vida':
      maximo, atual = equipamento.vida_maxima_efetiva(personagem), personagem.vida
    else:
      maximo, atual = equipamento.mana_maxima_efetiva(personagem), personagem.mana
    falta = maximo - atual
    if falta <= 0:
      escrever(f'Sua {recurso} já está no máximo.')
      continue

    quantidade = pedir_numero(f'Quanto de {recurso} deseja restaurar (máx {falta})? -->',
                               minimo=1, maximo=falta, entrada=entrada_texto, saida=escrever)
    custo = max(1, quantidade // 5)
    if not perguntar_sim_nao(f'Isso vai custar {custo} moedas de cobre. Confirmar?'):
      continue
    if personagem.moeda_cobre < custo:
      escrever('Você não tem moedas de cobre suficientes.')
      continue

    personagem.moeda_cobre -= custo
    if recurso == 'vida':
      personagem.vida += quantidade
    else:
      personagem.mana += quantidade
    escrever(f'{recurso.capitalize()} restaurada com sucesso!')


def tela_equipar_habilidades(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  while True:
    opcoes = [f'Slot {i + 1}: {nome} (equipada)'
              for i, nome in enumerate(personagem.habilidades_equipadas)]
    disponiveis = [nome for nome in personagem.habilidades_aprendidas
                   if nome not in personagem.habilidades_equipadas]
    opcoes += [f'Trocar por: {nome}' for nome in disponiveis]

    escolha = ler_acao('Habilidades equipadas', opcoes)
    if escolha is None or escolha < len(personagem.habilidades_equipadas):
      return

    nome_nova = disponiveis[escolha - len(personagem.habilidades_equipadas)]
    escolha_slot = ler_acao('Qual slot substituir?', personagem.habilidades_equipadas)
    if escolha_slot is None:
      continue
    antiga = personagem.habilidades_equipadas[escolha_slot]
    personagem.habilidades_equipadas[escolha_slot] = nome_nova
    escrever(f'Trocou {antiga} por {nome_nova}.')


def tela_status(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  while True:
    vida_max = equipamento.vida_maxima_efetiva(personagem)
    mana_max = equipamento.mana_maxima_efetiva(personagem)
    titulo = (f'Nível {personagem.nivel} — Exp {personagem.exp}/{personagem.exp_para_subir}\n'
              f'Vida: {personagem.vida}/{vida_max}   Mana: {personagem.mana}/{mana_max}\n'
              f'Poder: {personagem.poder}   Esquiva: {personagem.esquiva}%   Sorte: {personagem.sorte}\n'
              f'Pontos de status disponíveis: {personagem.pontos_status}')
    opcoes = ['+5 Vida máxima', '+5 Mana máxima', '+1 Poder', '+1 Sorte (crítico)', 'Equipar habilidades']
    escolha = ler_acao(titulo, opcoes)
    if escolha is None:
      return
    if escolha in (0, 1, 2, 3):
      if personagem.pontos_status < 1:
        escrever('Você não tem pontos de status disponíveis.')
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
      tela_equipar_habilidades(personagem, escrever, ler_acao)


def tela_personagem(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  while True:
    arma = equipamento.resolver_arma(personagem)
    armadura = equipamento.resolver_armadura(personagem)
    acessorio = equipamento.resolver_acessorio(personagem)
    titulo = (f'Arma: {arma.nome} ({arma.bonus_poder_percentual}% poder)\n'
              f'Armadura: {armadura.nome if armadura else "Nenhuma"}\n'
              f'Acessório: {acessorio.nome if acessorio else "Nenhum"}')

    opcoes = ([f'Equipar arma: {n}' for n in personagem.equipamentos_guardados] +
              [f'Equipar armadura: {n}' for n in personagem.armaduras_guardadas] +
              [f'Equipar acessório: {n}' for n in personagem.acessorios_guardados])
    if not opcoes:
      escrever('Você não tem nada guardado para trocar. Compre na loja.')
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
    escrever('Equipado com sucesso!')


def tela_guilda(personagem, escrever=print, ler_acao=None, _missoes_cache={}):
  ler_acao = ler_acao or menu_padrao
  if personagem.nome not in _missoes_cache:
    _missoes_cache[personagem.nome] = economia.gerar_missoes(personagem)
  while True:
    missoes = _missoes_cache[personagem.nome]
    opcoes = [f'Matar {m["quantidade"]}x {m["monstro"]} — {m["recompensa_exp"]} exp, '
              f'{m["recompensa_moedas"]} moedas' for m in missoes]
    opcoes.append('Renovar missões (100 moedas)')
    if personagem.missao_monstro:
      opcoes.append(f'Abandonar missão atual ({personagem.missao_monstro})')

    titulo = 'Guilda'
    if personagem.missao_monstro:
      titulo += (f'\nMissão ativa: matar {personagem.missao_monstro} '
                 f'({personagem.missao_quantidade_atual}/{personagem.missao_quantidade_alvo})')

    escolha = ler_acao(titulo, opcoes)
    if escolha is None:
      return
    if escolha < len(missoes):
      if personagem.missao_monstro:
        escrever('Você já está em uma missão. Abandone-a primeiro.')
        continue
      economia.aceitar_missao(personagem, missoes[escolha])
      escrever('Missão aceita!')
    elif escolha == len(missoes):
      if personagem.moeda_cobre < 100:
        escrever('Você não tem 100 moedas de cobre.')
        continue
      personagem.moeda_cobre -= 100
      _missoes_cache[personagem.nome] = economia.gerar_missoes(personagem)
      escrever('Missões renovadas.')
    else:
      economia.abandonar_missao(personagem)
      escrever('Missão abandonada.')


def tela_desbloquear_habilidades(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  while True:
    candidatas = [nome for nome in HABILIDADES_DESBLOQUEAVEIS.get(personagem.classe, [])
                  if nome not in personagem.habilidades_aprendidas]
    if not candidatas:
      escrever('Você já aprendeu todas as habilidades disponíveis para sua classe.')
      return
    opcoes = [f'{nome} — nível {HABILIDADES[nome].nivel_minimo}, {HABILIDADES[nome].preco} moedas'
              for nome in candidatas]
    escolha = ler_acao('Habilidades para desbloquear', opcoes)
    if escolha is None:
      return
    nome = candidatas[escolha]
    habilidade = HABILIDADES[nome]
    if personagem.nivel < habilidade.nivel_minimo:
      escrever('Você não tem nível suficiente.')
      continue
    if personagem.moeda_cobre < habilidade.preco:
      escrever('Você não tem moedas de cobre suficientes.')
      continue
    personagem.moeda_cobre -= habilidade.preco
    personagem.habilidades_aprendidas.append(nome)
    escrever(f'Você aprendeu {nome}! Equipe-a em Status -> Equipar Habilidades.')


def tela_bau(personagem, escrever=print, ler_acao=None, entrada_texto=input):
  ler_acao = ler_acao or menu_padrao
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
    _sucesso, mensagem = economia.converter(personagem, origem, destino, quantidade)
    escrever(mensagem)


def tela_mestre_habusken(personagem, escrever=print, ler_acao=None, entrada_texto=input, esperar=None):
  ler_acao = ler_acao or menu_padrao
  esperar = esperar or time.sleep
  if 'Slime Gigante' not in personagem.chefes_derrotados:
    escrever('O Mestre de Habusken não te reconhece como discípulo. '
              'Derrote o chefe do Andar 1 primeiro.')
    return
  while True:
    opcoes = [f'Treinar (50 moedas) — {personagem.treinamento_habusken}% concluído', 'Voltar']
    escolha = ler_acao('Mestre de Habusken', opcoes)
    if escolha is None or escolha == 1:
      return
    if personagem.moeda_cobre < 50:
      escrever('Você não tem 50 moedas de cobre.')
      continue
    personagem.moeda_cobre -= 50

    letras = [random.choice(string.ascii_uppercase) for _ in range(5)]
    escrever('Decore a sequência de letras a seguir:')
    for letra in letras:
      escrever(letra)
      esperar(1)
    resposta = entrada_texto('Digite as letras na ordem, separadas por espaço: -->')
    acertos = sum(1 for certa, digitada in zip(letras, resposta.upper().split()) if certa == digitada)
    personagem.treinamento_habusken = min(100, personagem.treinamento_habusken + acertos * 4)
    escrever(f'Você acertou {acertos} de {len(letras)} letras!')
    if personagem.treinamento_habusken >= 100 and not personagem.eten:
      personagem.eten = True
      escrever('Você concluiu o treinamento! Aprendeu Etén: +30% de dano em todos os ataques.')


def tela_crafting(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  receitas = list(RECEITAS.values())
  while True:
    opcoes = []
    for receita in receitas:
      requisitos = ', '.join(f'{qtd}x {nome}' for nome, qtd in receita.materiais_necessarios.items())
      opcoes.append(f'{receita.nome} (precisa: {requisitos})')
    escolha = ler_acao('Bancada de Trabalho', opcoes)
    if escolha is None:
      return
    sistema_crafting.craftar(personagem, receitas[escolha], escrever)
