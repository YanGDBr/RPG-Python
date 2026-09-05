"""Bancada de trabalho: materiais dropados por monstros viram poções e, com
material dos chefes finais, a arma lendária da classe do jogador e a
armadura abissal."""

from ..config import Cor
from ..dados.itens import ARMADURAS_UNICAS, ARMAS_LENDARIAS


def craftar(personagem, receita, escrever):
  for nome, quantidade in receita.materiais_necessarios.items():
    if personagem.materiais.get(nome, 0) < quantidade:
      escrever(f'{Cor.VERMELHO}Você não tem os materiais necessários para essa receita.{Cor.RESET}')
      return False

  for nome, quantidade in receita.materiais_necessarios.items():
    personagem.materiais[nome] -= quantidade
    if personagem.materiais[nome] <= 0:
      del personagem.materiais[nome]

  if receita.resultado_tipo == 'pocao_craftada':
    atual = personagem.pocoes.get(receita.resultado_nome, 0)
    personagem.pocoes[receita.resultado_nome] = atual + receita.quantidade_resultado
    escrever(f'{Cor.VERDE}Você craftou {receita.quantidade_resultado}x '
             f'Poção de {receita.resultado_nome}!{Cor.RESET}')
  elif receita.resultado_tipo == 'arma_lendaria':
    arma = ARMAS_LENDARIAS[receita.resultado_nome]
    personagem.equipamentos_guardados.append(arma.nome)
    escrever(f'{Cor.VERDE}Você forjou {arma.nome}! Equipe-a em Personagem.{Cor.RESET}')
  elif receita.resultado_tipo == 'armadura_unica':
    armadura = ARMADURAS_UNICAS[receita.resultado_nome]
    personagem.armaduras_guardadas.append(armadura.nome)
    escrever(f'{Cor.VERDE}Você forjou {armadura.nome}! Equipe-a em Personagem.{Cor.RESET}')

  return True
