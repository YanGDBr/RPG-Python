"""Recompensas de batalha, level-up e progresso de missão da guilda."""

import random
from datetime import datetime, timedelta
from math import trunc

from ..config import FOME_CRITICA, FOME_MAXIMA
from ..dados.itens import MATERIAIS
from ..dados.racas import RACAS
from .inventario import consumir_efeito_ativado


def verificar_morte(personagem, escrever):
  if personagem.vida > 0:
    return False
  personagem.morto = True
  personagem.momento_reviver = (datetime.now() + timedelta(minutes=5)).isoformat()
  escrever('Você morreu! Poderá reviver em 5 minutos.')
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
    escrever('Você está faminto! Isso está drenando sua vida.')
    personagem.vida = max(0, personagem.vida - 5)
  elif personagem.fome <= FOME_CRITICA:
    escrever('Sua fome está crítica — seus ataques causam menos dano até você comer.')


def conceder_recompensas(personagem, monstro_base, escrever):
  exp = random.randint(monstro_base.exp_min, monstro_base.exp_max)
  moedas = random.randint(monstro_base.moedas_min, monstro_base.moedas_max)

  bonus_drop = consumir_efeito_ativado(personagem, 'drop')
  if bonus_drop:
    exp = trunc(exp + exp * bonus_drop / 100)
    moedas = trunc(moedas + moedas * bonus_drop / 100)
    escrever('Recompensas aumentadas pelo Drop Buffer usado antes da batalha!')

  raca = RACAS.get(personagem.raca)
  if raca and raca.bonus_tipo == 'exp':
    exp = trunc(exp + exp * raca.valor / 100)
    escrever('Bônus de experiência da sua raça aplicado.')

  personagem.moeda_cobre += moedas
  personagem.exp += exp
  escrever(f'Você ganhou {exp} de experiência e {moedas} moedas de cobre.')

  for nome_item, chance in monstro_base.drops_item:
    if random.random() < chance:
      if nome_item in MATERIAIS:
        personagem.adicionar_material(nome_item)
      else:
        personagem.adicionar_item(nome_item)
      escrever(f'O {monstro_base.nome} deixou cair: {nome_item}!')

  if monstro_base.chefe and monstro_base.nome not in personagem.chefes_derrotados:
    personagem.chefes_derrotados.append(monstro_base.nome)

  subiu_nivel = False
  while personagem.exp >= personagem.exp_para_subir:
    personagem.exp -= personagem.exp_para_subir
    personagem.nivel += 1
    personagem.pontos_status += 3
    personagem.exp_para_subir = personagem.nivel * 50
    subiu_nivel = True
  if subiu_nivel:
    escrever(f'Você subiu para o nível {personagem.nivel}! Ganhou 3 pontos de status.')

  _verificar_missao(personagem, monstro_base, escrever)


def _verificar_missao(personagem, monstro_base, escrever):
  if personagem.missao_monstro != monstro_base.nome:
    return
  personagem.missao_quantidade_atual += 1
  if personagem.missao_quantidade_atual >= personagem.missao_quantidade_alvo:
    personagem.exp += personagem.missao_recompensa_exp
    personagem.moeda_cobre += personagem.missao_recompensa_moedas
    escrever(f'Missão concluída! Você ganhou {personagem.missao_recompensa_exp} de exp e '
             f'{personagem.missao_recompensa_moedas} moedas de cobre.')
    personagem.missao_monstro = ''
    personagem.missao_quantidade_alvo = 0
    personagem.missao_quantidade_atual = 0
    personagem.missao_recompensa_exp = 0
    personagem.missao_recompensa_moedas = 0
