"""Recompensas de batalha, level-up e progresso de missão da guilda."""

import random
from math import trunc

from ..config import (ACOES_POR_DESGASTE_FOME, BONUS_ELITE_RECOMPENSA_PERCENTUAL,
                       BONUS_PRIMEIRO_ABATE_CHEFE_PERCENTUAL, FOME_CRITICA,
                       FOME_MAXIMA, MULTIPLICADOR_EXP_GLOBAL, REPUTACAO_GANHA_POR_MISSAO, Cor)
from ..dados.itens import ACESSORIOS_UNICOS, MATERIAIS
from ..dados.racas import RACAS
from . import equipamento, sidequests as sistema_sidequests
from .inventario import consumir_efeito_ativado

# Documento de identidade liberado ao derrotar o chefe daquela dungeon pela
# primeira vez — é o que abre a passagem pelo guarda da próxima cidade no
# mundo aberto (ver rpg/sistemas/mundo.py e rpg/jogo.py). O texto de cada
# entrada é mostrado quando o documento é concedido.
ITENS_IDENTIDADE_POR_CHEFE = {
  'Dragão Ancião de Habusken': (
      'Selo de Habusken',
      'O conselho de Habusken sela seu feito com o brasão da vila: com o Dragão Ancião morto, '
      'você já não é só mais um aventureiro — é alguém que Vethgard vai reconhecer.'),
  'Kraken Ancestral': (
      'Selo de Vethgard',
      'A notícia chega a Vethgard antes de você: o Kraken Ancestral está morto. O selo que '
      'recebe carrega o peso disso — poucos o receberam, e menos ainda voltaram de onde ele leva.'),
}


def verificar_morte(personagem, escrever):
  """Morrer não tem mais tempo de espera — a punição (perder 1 nível e
  metade das moedas) é aplicada na hora, e o personagem já volta de pé,
  com pouca vida/mana/fome, pra vila."""
  if personagem.vida > 0:
    return False
  personagem.morto = True
  personagem.nivel = max(1, personagem.nivel - 1)
  personagem.exp = 0
  personagem.exp_para_subir = personagem.nivel * 50
  personagem.moeda_cobre //= 2
  personagem.moeda_prata //= 2
  personagem.moeda_ouro //= 2
  personagem.vida = 10
  personagem.mana = 10
  personagem.fome = 1
  personagem.efeitos_ativos.clear()
  personagem.local = 'vila'
  escrever(f'{Cor.VERMELHO}Você morreu! Perdeu 1 nível e metade das suas moedas, e voltou '
           f'para a vila com pouca vida, mana e fome.{Cor.RESET}')
  return True


def aplicar_desgaste_fome(personagem, escrever, limite_acoes=None):
  """Chamado a cada ação real (batalha/exploração) — a fome de 5 anos atrás só
  descia uma vez no login e nunca mais fazia diferença nenhuma. Só desgasta de
  fato 1 a cada `limite_acoes` ações (padrão: ACOES_POR_DESGASTE_FOME — dungeon
  usa isso; o mundo aberto passa ACOES_POR_DESGASTE_FOME_MUNDO, bem maior,
  porque lá desgasta por PASSO de verdade, bem mais frequente).

  Fome zerada dói, mas nunca mata: o mínimo de vida por inanição é 1 — só dá
  pra morrer perdendo uma luta de verdade, não por esquecer de comer."""
  limite_base = ACOES_POR_DESGASTE_FOME if limite_acoes is None else limite_acoes
  personagem.acoes_desde_desgaste_fome += 1
  limite = limite_base + equipamento.fome_lenta_acessorio(personagem)
  if personagem.acoes_desde_desgaste_fome < limite:
    return
  personagem.acoes_desde_desgaste_fome = 0
  personagem.fome = max(0, personagem.fome - 1)
  if personagem.fome <= 0:
    escrever(f'{Cor.VERMELHO}Você está faminto! Isso está drenando sua vida.{Cor.RESET}')
    personagem.vida = max(1, personagem.vida - 5)
  elif personagem.fome <= FOME_CRITICA:
    escrever(f'{Cor.AMARELO}Sua fome está crítica — seus ataques causam menos dano '
             f'até você comer.{Cor.RESET}')


def conceder_recompensas(personagem, monstro_base, escrever, elite=False):
  # Calculado ANTES de mexer em `chefes_derrotados` — depois disso a mesma
  # checagem já não seria mais verdadeira.
  primeiro_abate_de_chefe = monstro_base.chefe and monstro_base.nome not in personagem.chefes_derrotados

  exp = trunc(random.randint(monstro_base.exp_min, monstro_base.exp_max) * MULTIPLICADOR_EXP_GLOBAL)
  moedas = random.randint(monstro_base.moedas_min, monstro_base.moedas_max)

  if elite:
    exp = trunc(exp + exp * BONUS_ELITE_RECOMPENSA_PERCENTUAL / 100)
    moedas = trunc(moedas + moedas * BONUS_ELITE_RECOMPENSA_PERCENTUAL / 100)
    escrever(f'{Cor.AMARELO}Monstro elite! Recompensas em dobro.{Cor.RESET}')

  if primeiro_abate_de_chefe:
    exp = trunc(exp + exp * BONUS_PRIMEIRO_ABATE_CHEFE_PERCENTUAL / 100)
    moedas = trunc(moedas + moedas * BONUS_PRIMEIRO_ABATE_CHEFE_PERCENTUAL / 100)
    escrever(f'{Cor.AMARELO}Primeira vez derrotando {monstro_base.nome}! '
             f'Recompensas muito maiores por isso.{Cor.RESET}')

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

  if primeiro_abate_de_chefe:
    personagem.chefes_derrotados.append(monstro_base.nome)
    acessorio_unico = ACESSORIOS_UNICOS.get(monstro_base.nome)
    if acessorio_unico:
      personagem.acessorios_guardados.append(acessorio_unico.nome)
      escrever(f'{Cor.AMARELO}{monstro_base.nome} deixou cair um acessório único: '
               f'{acessorio_unico.nome}!{Cor.RESET}')
    entrada_documento = ITENS_IDENTIDADE_POR_CHEFE.get(monstro_base.nome)
    if entrada_documento:
      documento, flavor = entrada_documento
      personagem.adicionar_item_especial(documento)
      escrever(f'{Cor.CIANO}{flavor}{Cor.RESET}')
      escrever(f'{Cor.CIANO}Você recebeu um documento de identidade: {documento}!{Cor.RESET}')

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
  sistema_sidequests.registrar_derrota(personagem, monstro_base.nome, escrever)


def _verificar_missao(personagem, monstro_base, escrever):
  concluidas = []
  for missao in personagem.missoes_ativas:
    if missao['monstro'] != monstro_base.nome:
      continue
    missao['quantidade_atual'] += 1
    if missao['quantidade_atual'] >= missao['quantidade_alvo']:
      personagem.exp += missao['recompensa_exp']
      personagem.moeda_cobre += missao['recompensa_moedas']
      personagem.moedas_totais_ganhas += missao['recompensa_moedas']
      personagem.missoes_completadas += 1
      personagem.reputacao_guilda += REPUTACAO_GANHA_POR_MISSAO
      escrever(f'{Cor.VERDE}Missão concluída! Você ganhou {missao["recompensa_exp"]} de exp, '
               f'{missao["recompensa_moedas"]} cobres e {REPUTACAO_GANHA_POR_MISSAO} '
               f'de reputação com a guilda.{Cor.RESET}')
      concluidas.append(missao)
  for missao in concluidas:
    personagem.missoes_ativas.remove(missao)
