"""Recompensas de batalha, level-up e progresso de missão da guilda."""

import random
from datetime import datetime, timedelta
from math import trunc

from ..config import (BONUS_ELITE_RECOMPENSA_PERCENTUAL, FOME_CRITICA, FOME_MAXIMA,
                       REPUTACAO_GANHA_POR_MISSAO, Cor)
from ..dados.itens import ACESSORIOS_UNICOS, MATERIAIS
from ..dados.racas import RACAS
from . import equipamento
from .inventario import consumir_efeito_ativado


def verificar_morte(personagem, escrever):
  if personagem.vida > 0:
    return False
  personagem.morto = True
  personagem.momento_reviver = (datetime.now() + timedelta(minutes=5)).isoformat()
  escrever(f'{Cor.VERMELHO}Você morreu! Poderá reviver em 5 minutos.{Cor.RESET}')
  return True


def tentar_reviver(personagem):
  if not personagem.morto or personagem.momento_reviver is None:
    return False
  if datetime.now() >= datetime.fromisoformat(personagem.momento_reviver):
    personagem.morto = False
    personagem.momento_reviver = None
    personagem.vida = personagem.vida_maxima
    personagem.mana = personagem.mana_maxima
    return True
  return False


def aplicar_desgaste_fome(personagem, escrever):
  """Chamado a cada ação real (batalha/exploração) — a fome de 5 anos atrás só
  descia uma vez no login e nunca mais fazia diferença nenhuma."""
  personagem.fome = max(0, personagem.fome - 1)
  if personagem.fome <= 0:
    escrever(f'{Cor.VERMELHO}Você está faminto! Isso está drenando sua vida.{Cor.RESET}')
    personagem.vida = max(0, personagem.vida - 5)
  elif personagem.fome <= FOME_CRITICA:
    escrever(f'{Cor.AMARELO}Sua fome está crítica — seus ataques causam menos dano '
             f'até você comer.{Cor.RESET}')


def conceder_recompensas(personagem, monstro_base, escrever, elite=False):
  exp = random.randint(monstro_base.exp_min, monstro_base.exp_max)
  moedas = random.randint(monstro_base.moedas_min, monstro_base.moedas_max)

  if elite:
    exp = trunc(exp + exp * BONUS_ELITE_RECOMPENSA_PERCENTUAL / 100)
    moedas = trunc(moedas + moedas * BONUS_ELITE_RECOMPENSA_PERCENTUAL / 100)
    escrever(f'{Cor.AMARELO}Monstro elite! Recompensas em dobro.{Cor.RESET}')

  bonus_drop = consumir_efeito_ativado(personagem, 'drop')
  if bonus_drop:
    exp = trunc(exp + exp * bonus_drop / 100)
    moedas = trunc(moedas + moedas * bonus_drop / 100)
    escrever(f'{Cor.CIANO}Recompensas aumentadas pelo Drop Buffer usado antes da batalha!{Cor.RESET}')

  raca = RACAS.get(personagem.raca)
  if raca and raca.bonus_tipo == 'exp':
    exp = trunc(exp + exp * raca.valor / 100)
    escrever(f'{Cor.CIANO}Bônus de experiência da sua raça aplicado.{Cor.RESET}')

  bonus_exp_acessorio = equipamento.exp_extra_acessorio(personagem)
  if bonus_exp_acessorio:
    exp = trunc(exp + exp * bonus_exp_acessorio / 100)

  bonus_ouro_acessorio = equipamento.ouro_extra_acessorio(personagem)
  if bonus_ouro_acessorio:
    moedas = trunc(moedas + moedas * bonus_ouro_acessorio / 100)

  personagem.moeda_cobre += moedas
  personagem.moedas_totais_ganhas += moedas
  personagem.exp += exp
  personagem.monstros_derrotados += 1
  escrever(f'{Cor.VERDE}Você ganhou {exp} de experiência e {moedas} cobres.{Cor.RESET}')

  drops = list(monstro_base.drops_item)
  if elite:
    # monstro elite sempre garante pelo menos 1 drop, mesmo que a sorte falhe.
    drops = [(nome, 1.0) for nome, _chance in drops] or drops
  for nome_item, chance in drops:
    if random.random() < chance:
      if nome_item in MATERIAIS:
        personagem.adicionar_material(nome_item)
      elif nome_item in ACESSORIOS_UNICOS:
        personagem.acessorios_guardados.append(nome_item)
      else:
        personagem.adicionar_item(nome_item)
      escrever(f'{Cor.VERDE}O {monstro_base.nome} deixou cair: {nome_item}!{Cor.RESET}')

  if monstro_base.chefe and monstro_base.nome not in personagem.chefes_derrotados:
    personagem.chefes_derrotados.append(monstro_base.nome)
    acessorio_unico = ACESSORIOS_UNICOS.get(monstro_base.nome)
    if acessorio_unico:
      personagem.acessorios_guardados.append(acessorio_unico.nome)
      escrever(f'{Cor.AMARELO}{monstro_base.nome} deixou cair um acessório único: '
               f'{acessorio_unico.nome}!{Cor.RESET}')

  subiu_nivel = False
  while personagem.exp >= personagem.exp_para_subir:
    personagem.exp -= personagem.exp_para_subir
    personagem.nivel += 1
    personagem.pontos_status += 3
    personagem.exp_para_subir = personagem.nivel * 50
    subiu_nivel = True
  if subiu_nivel:
    escrever(f'{Cor.VERDE}Você subiu para o nível {personagem.nivel}! '
             f'Ganhou 3 pontos de status.{Cor.RESET}')

  _verificar_missao(personagem, monstro_base, escrever)


def _verificar_missao(personagem, monstro_base, escrever):
  if personagem.missao_monstro != monstro_base.nome:
    return
  personagem.missao_quantidade_atual += 1
  if personagem.missao_quantidade_atual >= personagem.missao_quantidade_alvo:
    personagem.exp += personagem.missao_recompensa_exp
    personagem.moeda_cobre += personagem.missao_recompensa_moedas
    personagem.moedas_totais_ganhas += personagem.missao_recompensa_moedas
    personagem.missoes_completadas += 1
    personagem.reputacao_guilda += REPUTACAO_GANHA_POR_MISSAO
    escrever(f'{Cor.VERDE}Missão concluída! Você ganhou {personagem.missao_recompensa_exp} de exp, '
             f'{personagem.missao_recompensa_moedas} cobres e {REPUTACAO_GANHA_POR_MISSAO} '
             f'de reputação com a guilda.{Cor.RESET}')
    personagem.missao_monstro = ''
    personagem.missao_quantidade_alvo = 0
    personagem.missao_quantidade_atual = 0
    personagem.missao_recompensa_exp = 0
    personagem.missao_recompensa_moedas = 0
