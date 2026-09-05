"""Todas as telas da Vila Habusken que não são a loja nem a dungeon."""

import random
import string
import time

from ..config import (BONUS_ETEN_PERCENTUAL, CUSTO_RENOVAR_QUADRO,
                       ENCANTAMENTO_CUSTO_PRATA_BASE, ENCANTAMENTO_INCREMENTO,
                       ENCANTAMENTO_MATERIAL, ENCANTAMENTO_MAXIMO_ARMADURA,
                       ENCANTAMENTO_MAXIMO_ARMA, MAX_MISSOES_ATIVAS,
                       REPUTACAO_TIERS, Cor)
from ..dados.dungeons import DUNGEONS
from ..dados.especializacoes import (ESPECIALIZACOES, ESPECIALIZACOES_POR_CLASSE,
                                      NIVEL_MINIMO_ESPECIALIZACAO)
from ..dados.habilidades import HABILIDADES, HABILIDADES_DESBLOQUEAVEIS
from ..dados.receitas import RECEITAS
from ..entrada import aguardar_leitura
from ..entrada import menu as menu_padrao
from ..entrada import pedir_numero, perguntar_sim_nao
from ..interface import limpar_tela, ljust_visivel
from . import crafting as sistema_crafting
from . import economia, equipamento, inventario


def _titulo(personagem, texto):
  return f'{equipamento.resumo_status(personagem)}\n\n{texto}'


def tela_casa(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    opcoes = ['Descansar (recupera tudo, 1x por nível)', 'Comer', 'Voltar']
    escolha = ler_acao(_titulo(personagem, 'Casa'), opcoes)
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
    opcoes = [f'Restaurar {Cor.VERMELHO}vida{Cor.RESET} (1 cobre a cada 5 de vida)',
              f'Restaurar {Cor.AZUL}mana{Cor.RESET} (1 cobre a cada 5 de mana)', 'Voltar']
    escolha = ler_acao(_titulo(personagem, 'Curandeira'), opcoes)
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
    if not perguntar_sim_nao(f'Isso vai custar {custo} cobres. Confirmar?'):
      continue
    if personagem.moeda_cobre < custo:
      escrever(f'{Cor.VERMELHO}Você não tem cobres suficientes.{Cor.RESET}')
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

    escolha = ler_acao(_titulo(personagem, 'Habilidades equipadas'), opcoes)
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
    titulo = (f'{equipamento.resumo_status(personagem)}\n\n'
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
    titulo = (f'{equipamento.resumo_status(personagem)}\n\n'
              f'Arma: {Cor.BRANCO}{arma.nome}{Cor.RESET} ({arma.bonus_poder_percentual}% poder)\n'
              f'Armadura: {Cor.BRANCO}{armadura.nome if armadura else "Nenhuma"}{Cor.RESET}\n'
              f'Acessório: {Cor.BRANCO}{acessorio.nome if acessorio else "Nenhum"}{Cor.RESET}')

    opcoes = ([f'Equipar arma: {n}' for n in personagem.equipamentos_guardados] +
              [f'Equipar armadura: {n}' for n in personagem.armaduras_guardadas] +
              [f'Equipar acessório: {n}' for n in personagem.acessorios_guardados])
    if not opcoes:
      # Antes isso só mostrava um erro e saía, sem nunca exibir o `titulo`
      # (que tem o equipamento atual) — parecia que o equipar tinha falhado,
      # mesmo quando tinha funcionado normalmente.
      titulo_vazio = (f'{titulo}\n\n'
                      f'{Cor.CIANO}Nada guardado pra trocar agora. Compre mais na loja.{Cor.RESET}')
      ler_acao(titulo_vazio, ['Voltar'], com_voltar=False)
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


_LARGURA_QUADRO = 58


def _linha_quadro(texto):
  return f'|{ljust_visivel(" " + texto, _LARGURA_QUADRO - 2)}|'


def _desenhar_quadro(titulo, linhas):
  borda = '+' + '-' * (_LARGURA_QUADRO - 2) + '+'
  corpo = [borda, _linha_quadro(f'{Cor.BRANCO}{titulo}{Cor.RESET}'), borda]
  for linha in linhas:
    corpo.append(_linha_quadro(linha))
  corpo.append(borda)
  return '\n'.join(corpo)


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
    escolha = ler_acao(titulo, opcoes)
    if escolha is None:
      return
    _tela_quadro_andares(personagem, dungeons_disponiveis[escolha], escrever, ler_acao, aguardar,
                          _quadros_cache)


def _tela_quadro_andares(personagem, dungeon_id, escrever, ler_acao, aguardar, quadros_cache):
  dungeon = DUNGEONS[dungeon_id]
  while True:
    maior = max(personagem.maior_andar_visitado.get(dungeon_id, 1),
                personagem.andar_atual.get(dungeon_id, 1))
    opcoes = [f'Andar {n} — {dungeon.andares[n - 1].nome}' for n in range(1, maior + 1)]
    titulo = (f'{Cor.ROSA}Guilda — {dungeon.nome}{Cor.RESET}\n\n'
              f'Só existe quadro de missões dos andares que você já pisou.\n'
              f'Escolha um andar:')
    escolha = ler_acao(titulo, opcoes)
    if escolha is None:
      return
    _tela_quadro_missoes(personagem, dungeon_id, escolha + 1, escrever, ler_acao, aguardar, quadros_cache)


def _tela_quadro_missoes(personagem, dungeon_id, andar_numero, escrever, ler_acao, aguardar, quadros_cache):
  chave = (personagem.nome, dungeon_id, andar_numero)
  if chave not in quadros_cache:
    quadros_cache[chave] = economia.gerar_missoes_do_andar(personagem, dungeon_id, andar_numero)

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

    escolha = ler_acao(titulo, opcoes)
    if escolha is None:
      return

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
  while True:
    candidatas = [nome for nome in HABILIDADES_DESBLOQUEAVEIS.get(personagem.classe, [])
                  if nome not in personagem.habilidades_aprendidas]
    if not candidatas:
      escrever(f'{Cor.CIANO}Você já aprendeu todas as habilidades disponíveis para sua classe.{Cor.RESET}')
      aguardar()
      return
    opcoes = [f'{Cor.BRANCO}{nome}{Cor.RESET} — nível {HABILIDADES[nome].nivel_minimo}, '
              f'{HABILIDADES[nome].preco} cobres' for nome in candidatas]
    escolha = ler_acao(_titulo(personagem, 'Habilidades para desbloquear'), opcoes)
    if escolha is None:
      return
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
    escolha = ler_acao(_titulo(personagem, 'Ferreiro — Encantamento'), opcoes)
    if escolha is None:
      return
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


def tela_bau(personagem, escrever=print, ler_acao=None, entrada_texto=input, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    titulo = (f'{equipamento.resumo_status(personagem)}\n\n'
              f'Cobres: {personagem.moeda_cobre}\n'
              f'Pratas: {personagem.moeda_prata}\n'
              f'Ouros: {personagem.moeda_ouro}')
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
  while True:
    opcoes = [f'Treinar (50 cobres) — {personagem.treinamento_habusken}% concluído', 'Voltar']
    escolha = ler_acao(_titulo(personagem, 'Mestre de Habusken'), opcoes)
    if escolha is None or escolha == 1:
      return
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
  while True:
    opcoes = []
    for receita in receitas:
      requisitos = ', '.join(f'{qtd}x {nome}' for nome, qtd in receita.materiais_necessarios.items())
      opcoes.append(f'{Cor.BRANCO}{receita.nome}{Cor.RESET} (precisa: {requisitos})')
    escolha = ler_acao(_titulo(personagem, 'Bancada de Trabalho'), opcoes)
    if escolha is None:
      return
    sistema_crafting.craftar(personagem, receitas[escolha], escrever)
    aguardar()
