"""Consumo de poções, itens comuns e comida (fora de combate ou durante ele)."""

from ..config import FOME_MAXIMA, Cor
from ..dados.itens import ITENS_CONSUMIVEIS, POCOES, POCOES_CRAFTADAS
from . import equipamento


def usar_pocao(personagem, nome_pocao, em_batalha, escrever):
  quantidade = personagem.pocoes.get(nome_pocao, 0)
  if quantidade <= 0:
    escrever(f'{Cor.VERMELHO}Você não tem essa poção.{Cor.RESET}')
    return False

  dado = POCOES.get(nome_pocao) or POCOES_CRAFTADAS.get(nome_pocao)
  if dado is None:
    escrever(f'{Cor.VERMELHO}Poção desconhecida.{Cor.RESET}')
    return False

  if dado.efeito == 'vida':
    maximo = equipamento.vida_maxima_efetiva(personagem)
    personagem.vida = min(maximo, personagem.vida + dado.valor)
    escrever(f'{Cor.VERMELHO}Você recuperou {dado.valor} de vida.{Cor.RESET}')
  elif dado.efeito == 'mana':
    maximo = equipamento.mana_maxima_efetiva(personagem)
    personagem.mana = min(maximo, personagem.mana + dado.valor)
    escrever(f'{Cor.AZUL}Você recuperou {dado.valor} de mana.{Cor.RESET}')
  elif dado.efeito == 'esquiva':
    if not em_batalha:
      escrever(f'{Cor.VERMELHO}Essa poção só pode ser usada em batalha.{Cor.RESET}')
      return False
    if personagem.pocao_esquiva_usada:
      escrever(f'{Cor.VERMELHO}Você já usou uma poção de esquiva nesta batalha.{Cor.RESET}')
      return False
    personagem.bonus_esquiva_batalha += dado.valor
    personagem.pocao_esquiva_usada = True
    escrever(f'{Cor.AMARELO}Sua esquiva aumentou {dado.valor} pontos até o fim da batalha.{Cor.RESET}')
  elif dado.efeito == 'poder':
    if not em_batalha:
      escrever(f'{Cor.VERMELHO}Essa poção só pode ser usada em batalha.{Cor.RESET}')
      return False
    if personagem.pocao_poder_usada:
      escrever(f'{Cor.VERMELHO}Você já usou uma poção de poder nesta batalha.{Cor.RESET}')
      return False
    personagem.bonus_dano_batalha += dado.valor
    personagem.pocao_poder_usada = True
    escrever(f'{Cor.VERMELHO}Seu dano aumentou {dado.valor}% até o fim da batalha.{Cor.RESET}')
  elif dado.efeito == 'critico':
    if not em_batalha:
      escrever(f'{Cor.VERMELHO}Essa poção só pode ser usada em batalha.{Cor.RESET}')
      return False
    if personagem.pocao_furia_usada:
      escrever(f'{Cor.VERMELHO}Você já usou uma poção de fúria nesta batalha.{Cor.RESET}')
      return False
    personagem.bonus_critico_batalha += dado.valor
    personagem.pocao_furia_usada = True
    escrever(f'{Cor.AMARELO}Sua chance de crítico aumentou {dado.valor}% até o fim da batalha.{Cor.RESET}')

  personagem.pocoes[nome_pocao] -= 1
  if personagem.pocoes[nome_pocao] <= 0:
    del personagem.pocoes[nome_pocao]
  return True


def usar_item_consumivel(personagem, nome_item, escrever):
  if personagem.inventario.get(nome_item, 0) <= 0:
    escrever(f'{Cor.VERMELHO}Você não tem esse item.{Cor.RESET}')
    return False
  dado = ITENS_CONSUMIVEIS[nome_item]

  conflitos = {'anti_monstro': 'monstro', 'monstro': 'anti_monstro'}
  conflito = conflitos.get(dado.tipo)
  if conflito and any(ativo['tipo'] == conflito for ativo in personagem.itens_ativados):
    escrever(f'{Cor.VERMELHO}Você está sob um efeito conflitante — '
             f'não é possível usar {nome_item} agora.{Cor.RESET}')
    return False

  personagem.itens_ativados.append({'tipo': dado.tipo, 'valor': dado.valor})
  personagem.remover_item(nome_item, 1)
  escrever(f'{Cor.VERDE}Você usou {nome_item}. O efeito vale pela próxima exploração.{Cor.RESET}')
  return True


def consumir_efeito_ativado(personagem, tipo):
  """Procura e remove (consome) o primeiro item ativado do tipo dado, devolvendo
  seu valor — ou None se não houver nenhum. Usado uma vez e some, como no jogo
  original (o efeito 'vale' pela próxima exploração/batalha)."""
  for ativo in personagem.itens_ativados:
    if ativo['tipo'] == tipo:
      personagem.itens_ativados.remove(ativo)
      return ativo['valor']
  return None


def comer(personagem, nome_comida, escrever):
  if personagem.comidas.get(nome_comida, 0) <= 0:
    escrever(f'{Cor.VERMELHO}Você não tem essa comida.{Cor.RESET}')
    return False
  personagem.comidas[nome_comida] -= 1
  personagem.fome = FOME_MAXIMA
  escrever(f'{Cor.VERDE}Você comeu {nome_comida} e recuperou sua fome.{Cor.RESET}')
  return True
