"""Telas de loja. Todas usam o mesmo `menu()` de setas e a mesma função de
pagamento — no original cada categoria de loja tinha seu próprio bloco de
código quase idêntico, com preços que às vezes nem batiam com o texto exibido.
"""

from ..dados.itens import PRECO_COMIDA
from ..dados.lojas import (CATALOGO_ACESSORIOS, CATALOGO_ARMADURAS,
                            CATALOGO_ITENS_CONSUMIVEIS, CATALOGO_POCOES,
                            COMIDAS_VENDIDAS, armas_disponiveis_para_classe)
from ..entrada import menu as menu_padrao


def _pagar(personagem, preco, escrever):
  if personagem.moeda_cobre < preco:
    escrever('Você não tem moedas de cobre suficientes.')
    return False
  personagem.moeda_cobre -= preco
  return True


def loja_pocoes(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  while True:
    opcoes = [f'Poção de {p.nome} — {p.preco} moedas de cobre' for p in CATALOGO_POCOES]
    escolha = ler_acao('Loja de Poções', opcoes)
    if escolha is None:
      return
    pocao = CATALOGO_POCOES[escolha]
    if _pagar(personagem, pocao.preco, escrever):
      personagem.pocoes[pocao.nome] = personagem.pocoes.get(pocao.nome, 0) + 1
      escrever(f'Você comprou uma Poção de {pocao.nome}.')


def loja_armaduras(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  while True:
    opcoes = [f'{a.nome} — {a.preco} moedas ({a.descricao})' for a in CATALOGO_ARMADURAS]
    escolha = ler_acao('Loja de Armaduras', opcoes)
    if escolha is None:
      return
    armadura = CATALOGO_ARMADURAS[escolha]
    if armadura.nome in personagem.armaduras_guardadas or personagem.armadura_equipada == armadura.nome:
      escrever('Você já tem essa armadura.')
      continue
    if _pagar(personagem, armadura.preco, escrever):
      personagem.armaduras_guardadas.append(armadura.nome)
      escrever(f'Você comprou {armadura.nome}. Equipe-a em Personagem.')


def loja_itens(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  while True:
    opcoes = ([f'{a.nome} — {a.preco} moedas ({a.descricao})' for a in CATALOGO_ACESSORIOS] +
              [f'{i.nome} — {i.preco} moedas ({i.descricao})' for i in CATALOGO_ITENS_CONSUMIVEIS] +
              [f'{c} — {PRECO_COMIDA} moedas' for c in COMIDAS_VENDIDAS])
    escolha = ler_acao('Loja de Itens/Acessórios/Comida', opcoes)
    if escolha is None:
      return

    total_acessorios = len(CATALOGO_ACESSORIOS)
    total_itens = len(CATALOGO_ITENS_CONSUMIVEIS)

    if escolha < total_acessorios:
      acessorio = CATALOGO_ACESSORIOS[escolha]
      if acessorio.nome in personagem.acessorios_guardados or personagem.acessorio_equipado == acessorio.nome:
        escrever('Você já tem esse acessório.')
        continue
      if _pagar(personagem, acessorio.preco, escrever):
        personagem.acessorios_guardados.append(acessorio.nome)
        escrever(f'Você comprou {acessorio.nome}. Equipe-o em Personagem.')
    elif escolha < total_acessorios + total_itens:
      item = CATALOGO_ITENS_CONSUMIVEIS[escolha - total_acessorios]
      if _pagar(personagem, item.preco, escrever):
        personagem.adicionar_item(item.nome)
        escrever(f'Você comprou {item.nome}.')
    else:
      nome_comida = COMIDAS_VENDIDAS[escolha - total_acessorios - total_itens]
      if _pagar(personagem, PRECO_COMIDA, escrever):
        personagem.comidas[nome_comida] = personagem.comidas.get(nome_comida, 0) + 1
        escrever(f'Você comprou {nome_comida}.')


def loja_equipamentos(personagem, escrever=print, ler_acao=None):
  ler_acao = ler_acao or menu_padrao
  while True:
    armas = [a for a in armas_disponiveis_para_classe(personagem.classe)
             if a.nivel_minimo <= personagem.nivel]
    if not armas:
      escrever('Nenhum equipamento novo disponível para o seu nível ainda.')
      return
    opcoes = [f'{a.nome} — {a.preco} moedas ({a.bonus_poder_percentual}% de poder)' for a in armas]
    escolha = ler_acao('Loja de Equipamentos', opcoes)
    if escolha is None:
      return
    arma = armas[escolha]
    if arma.nome in personagem.equipamentos_guardados or personagem.arma_equipada == arma.nome:
      escrever('Você já tem essa arma.')
      continue
    if _pagar(personagem, arma.preco, escrever):
      personagem.equipamentos_guardados.append(arma.nome)
      escrever(f'Você comprou {arma.nome}. Equipe-a em Personagem.')
