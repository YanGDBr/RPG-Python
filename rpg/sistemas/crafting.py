"""Bancada de trabalho: materiais dropados por monstros viram poções e, com
material dos dois chefes finais, a arma lendária da classe do jogador."""

from ..dados.itens import ARMAS_LENDARIAS


def craftar(personagem, receita, escrever):
  for nome, quantidade in receita.materiais_necessarios.items():
    if personagem.materiais.get(nome, 0) < quantidade:
      escrever('Você não tem os materiais necessários para essa receita.')
      return False

  for nome, quantidade in receita.materiais_necessarios.items():
    personagem.materiais[nome] -= quantidade
    if personagem.materiais[nome] <= 0:
      del personagem.materiais[nome]

  if receita.resultado_tipo == 'pocao_craftada':
    atual = personagem.pocoes.get(receita.resultado_nome, 0)
    personagem.pocoes[receita.resultado_nome] = atual + receita.quantidade_resultado
    escrever(f'Você craftou {receita.quantidade_resultado}x Poção de {receita.resultado_nome}!')
  elif receita.resultado_tipo == 'arma_lendaria':
    arma = ARMAS_LENDARIAS[receita.resultado_nome]
    personagem.equipamentos_guardados.append(arma.nome)
    escrever(f'Você forjou {arma.nome}! Equipe-a em Personagem.')

  return True
