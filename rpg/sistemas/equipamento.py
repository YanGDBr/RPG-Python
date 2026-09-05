"""Resolve nome-do-item-equipado -> objeto de dado, e calcula os bônus efetivos.

No jogo original, os efeitos de acessório (Pulseira Sagrada aumentar vida/mana,
Anel de Fogo aplicar queimadura) praticamente nunca eram checados em lugar
nenhum — só o acessório de "achar sala do chefe" funcionava de verdade. Aqui
tudo passa por estas funções, então nenhum bônus fica esquecido.
"""

from ..config import Cor
from ..dados.classes import CLASSES
from ..dados.itens import ACESSORIOS, ACESSORIOS_UNICOS, ARMADURAS, ARMADURAS_UNICAS, ARMAS, ARMAS_LENDARIAS


def resolver_arma(personagem):
  arma_inicial = CLASSES[personagem.classe].arma_inicial
  nome = personagem.arma_equipada or arma_inicial.nome
  if nome == arma_inicial.nome:
    return arma_inicial
  if nome in ARMAS:
    return ARMAS[nome]
  for arma in ARMAS_LENDARIAS.values():
    if arma.nome == nome:
      return arma
  return arma_inicial


def bonus_poder_arma_efetivo(personagem):
  """Bônus de poder da arma equipada + o que já foi encantado nela."""
  return resolver_arma(personagem).bonus_poder_percentual + personagem.encantamento_arma


def resolver_armadura(personagem):
  return ARMADURAS.get(personagem.armadura_equipada) or ARMADURAS_UNICAS.get(personagem.armadura_equipada)


def resolver_acessorios(personagem):
  """Todos os acessórios equipados, já resolvidos — o personagem tem, por
  padrão, 1 slot, e pode comprar até 3 a mais (ver CUSTOS_SLOT_ACESSORIO)."""
  resolvidos = []
  for nome in personagem.acessorios_equipados:
    acessorio = ACESSORIOS.get(nome) or ACESSORIOS_UNICOS.get(nome)
    if acessorio:
      resolvidos.append(acessorio)
  return resolvidos


def _soma_acessorios(personagem, efeito):
  """A maioria dos bônus de acessório é aditiva — com vários slots, dá pra
  empilhar o mesmo tipo de efeito de acessórios diferentes."""
  return sum(a.valor for a in resolver_acessorios(personagem) if a.efeito == efeito)


def vida_maxima_efetiva(personagem):
  base = personagem.vida_maxima
  armadura = resolver_armadura(personagem)
  bonus_percentual = (armadura.bonus_vida_percentual if armadura else 0) + personagem.encantamento_armadura
  bonus_fixo = _soma_acessorios(personagem, 'mana_vida')
  return round(base + base * bonus_percentual / 100) + bonus_fixo


def mana_maxima_efetiva(personagem):
  base = personagem.mana_maxima
  armadura = resolver_armadura(personagem)
  bonus_percentual = armadura.bonus_mana_percentual if armadura else 0
  bonus_fixo = _soma_acessorios(personagem, 'mana_vida')
  return round(base + base * bonus_percentual / 100) + bonus_fixo


def chance_critico_extra_acessorio(personagem):
  return _soma_acessorios(personagem, 'critico')


def chance_boss_extra_acessorio(personagem):
  """O efeito 'boss' guarda o divisor final da rolagem de achar chefe (menor
  = mais frequente) — com vários acessórios desse tipo, vale o melhor (o
  menor divisor), nunca soma (não faria sentido somar divisores)."""
  valores = [a.valor for a in resolver_acessorios(personagem) if a.efeito == 'boss']
  return min(valores) if valores else 0


def reducao_dano_acessorio(personagem):
  return _soma_acessorios(personagem, 'reducao_dano')


def esquiva_flat_acessorio(personagem):
  return _soma_acessorios(personagem, 'esquiva_flat')


def exp_extra_acessorio(personagem):
  return _soma_acessorios(personagem, 'exp_extra')


def ouro_extra_acessorio(personagem):
  return _soma_acessorios(personagem, 'ouro_extra')


def regeneracao_acessorio(personagem):
  return _soma_acessorios(personagem, 'regeneracao')


def efeitos_iniciais_de_batalha_acessorios(personagem):
  """Anel de Fogo (e qualquer outro acessório igual): aplica Queimadura no
  monstro assim que a batalha começa — devolve um por acessório equipado com
  esse efeito, já que agora pode haver mais de um slot."""
  return [('Queimadura', a.valor) for a in resolver_acessorios(personagem)
          if a.efeito == 'queimadura_inicial']


def resumo_status(personagem):
  """Uma linha compacta com nível/exp/vida/mana/saldo — usada no topo de quase
  toda tela, pra nunca precisar entrar em outro menu só pra conferir isso."""
  vida_max = vida_maxima_efetiva(personagem)
  mana_max = mana_maxima_efetiva(personagem)
  return (f'{Cor.BRANCO}Nv.{personagem.nivel}{Cor.RESET} '
          f'(Exp {personagem.exp}/{personagem.exp_para_subir})  '
          f'{Cor.VERMELHO}Vida {personagem.vida}/{vida_max}{Cor.RESET}  '
          f'{Cor.AZUL}Mana {personagem.mana}/{mana_max}{Cor.RESET}  '
          f'{Cor.AMARELO}{personagem.moeda_cobre} cobres{Cor.RESET}')
