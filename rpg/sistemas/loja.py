"""Telas de loja. Todas usam o mesmo `menu()` de setas e a mesma função de
pagamento — no original cada categoria de loja tinha seu próprio bloco de
código quase idêntico, com preços que às vezes nem batiam com o texto exibido.
"""

import random
from datetime import date

from ..config import DESCONTO_OFERTA_DIA, QUANTIDADE_OFERTAS_DIA, Cor
from ..dados.itens import PRECO_COMIDA
from ..dados.lojas import (CATALOGO_ACESSORIOS, CATALOGO_ARMADURAS,
                            CATALOGO_ITENS_CONSUMIVEIS, CATALOGO_POCOES,
                            COMIDAS_VENDIDAS, armas_disponiveis_para_classe)
from ..entrada import aguardar_leitura
from ..entrada import menu as menu_padrao
from ..modelos.item import Acessorio, ItemConsumivel, Pocao
from . import equipamento


def _titulo(personagem, texto):
  return f'{equipamento.resumo_status(personagem)}\n\n{texto}'


def _pagar(personagem, preco, escrever):
  if personagem.moeda_cobre < preco:
    escrever(f'{Cor.VERMELHO}Você não tem cobres suficientes.{Cor.RESET}')
    return False
  personagem.moeda_cobre -= preco
  return True


def loja_pocoes(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    opcoes = [f'Poção de {p.nome} — {p.preco} cobres' for p in CATALOGO_POCOES]
    escolha = ler_acao(_titulo(personagem, 'Loja de Poções'), opcoes)
    if escolha is None:
      return
    pocao = CATALOGO_POCOES[escolha]
    if _pagar(personagem, pocao.preco, escrever):
      personagem.pocoes[pocao.nome] = personagem.pocoes.get(pocao.nome, 0) + 1
      escrever(f'{Cor.VERDE}Você comprou uma Poção de {pocao.nome}.{Cor.RESET}')
    aguardar()


def loja_armaduras(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    opcoes = [f'{a.nome} — {a.preco} cobres ({a.descricao})' for a in CATALOGO_ARMADURAS]
    escolha = ler_acao(_titulo(personagem, 'Loja de Armaduras'), opcoes)
    if escolha is None:
      return
    armadura = CATALOGO_ARMADURAS[escolha]
    if armadura.nome in personagem.armaduras_guardadas or personagem.armadura_equipada == armadura.nome:
      escrever(f'{Cor.AMARELO}Você já tem essa armadura.{Cor.RESET}')
      aguardar()
      continue
    if _pagar(personagem, armadura.preco, escrever):
      personagem.armaduras_guardadas.append(armadura.nome)
      escrever(f'{Cor.VERDE}Você comprou {armadura.nome}. Equipe-a em Personagem.{Cor.RESET}')
    aguardar()


def loja_acessorios(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    opcoes = [f'{a.nome} — {a.preco} cobres ({a.descricao}) — equipe em Personagem'
              for a in CATALOGO_ACESSORIOS]
    escolha = ler_acao(_titulo(personagem, 'Loja de Acessórios'), opcoes)
    if escolha is None:
      return
    acessorio = CATALOGO_ACESSORIOS[escolha]
    if (acessorio.nome in personagem.acessorios_guardados
        or acessorio.nome in personagem.acessorios_equipados):
      escrever(f'{Cor.AMARELO}Você já tem esse acessório.{Cor.RESET}')
      aguardar()
      continue
    if _pagar(personagem, acessorio.preco, escrever):
      personagem.acessorios_guardados.append(acessorio.nome)
      escrever(f'{Cor.VERDE}Você comprou {acessorio.nome}. Equipe-o em Personagem.{Cor.RESET}')
    aguardar()


def loja_itens_consumiveis(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    opcoes = [f'{i.nome} — {i.preco} cobres ({i.descricao}) — use no Inventário'
              for i in CATALOGO_ITENS_CONSUMIVEIS]
    escolha = ler_acao(_titulo(personagem, 'Loja de Itens'), opcoes)
    if escolha is None:
      return
    item = CATALOGO_ITENS_CONSUMIVEIS[escolha]
    if _pagar(personagem, item.preco, escrever):
      personagem.adicionar_item(item.nome)
      escrever(f'{Cor.VERDE}Você comprou {item.nome}.{Cor.RESET}')
    aguardar()


def loja_comidas(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    opcoes = [f'{c} — {PRECO_COMIDA} cobres' for c in COMIDAS_VENDIDAS]
    escolha = ler_acao(_titulo(personagem, 'Loja de Comidas'), opcoes)
    if escolha is None:
      return
    nome_comida = COMIDAS_VENDIDAS[escolha]
    if _pagar(personagem, PRECO_COMIDA, escrever):
      personagem.comidas[nome_comida] = personagem.comidas.get(nome_comida, 0) + 1
      escrever(f'{Cor.VERDE}Você comprou {nome_comida}.{Cor.RESET}')
    aguardar()


def _ofertas_do_dia():
  pool = list(CATALOGO_POCOES) + list(CATALOGO_ITENS_CONSUMIVEIS) + list(CATALOGO_ACESSORIOS)
  gerador = random.Random(date.today().toordinal())
  return gerador.sample(pool, k=min(QUANTIDADE_OFERTAS_DIA, len(pool)))


def _preco_com_desconto(preco):
  return max(1, round(preco * (1 - DESCONTO_OFERTA_DIA / 100)))


def loja_ofertas_do_dia(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  ofertas = _ofertas_do_dia()
  while True:
    opcoes = [f'{item.nome} — {Cor.CINZA}{item.preco}{Cor.RESET} '
              f'{Cor.VERDE}{_preco_com_desconto(item.preco)} cobres{Cor.RESET} '
              f'({DESCONTO_OFERTA_DIA}% off)' for item in ofertas]
    titulo = _titulo(personagem, f'Ofertas do Dia ({date.today().isoformat()})')
    escolha = ler_acao(titulo, opcoes)
    if escolha is None:
      return
    item = ofertas[escolha]
    preco_final = _preco_com_desconto(item.preco)
    if isinstance(item, Acessorio):
      if item.nome in personagem.acessorios_guardados or item.nome in personagem.acessorios_equipados:
        escrever(f'{Cor.AMARELO}Você já tem esse acessório.{Cor.RESET}')
        aguardar()
        continue
      if _pagar(personagem, preco_final, escrever):
        personagem.acessorios_guardados.append(item.nome)
        escrever(f'{Cor.VERDE}Você comprou {item.nome}. Equipe-o em Personagem.{Cor.RESET}')
    elif isinstance(item, Pocao):
      if _pagar(personagem, preco_final, escrever):
        personagem.pocoes[item.nome] = personagem.pocoes.get(item.nome, 0) + 1
        escrever(f'{Cor.VERDE}Você comprou uma Poção de {item.nome}.{Cor.RESET}')
    elif isinstance(item, ItemConsumivel):
      if _pagar(personagem, preco_final, escrever):
        personagem.adicionar_item(item.nome)
        escrever(f'{Cor.VERDE}Você comprou {item.nome}.{Cor.RESET}')
    aguardar()


def loja_equipamentos(personagem, escrever=print, ler_acao=None, aguardar=None):
  ler_acao = ler_acao or menu_padrao
  aguardar = aguardar or aguardar_leitura
  while True:
    armas = [a for a in armas_disponiveis_para_classe(personagem.classe)
             if a.nivel_minimo <= personagem.nivel]
    if not armas:
      escrever(f'{Cor.AMARELO}Nenhum equipamento novo disponível para o seu nível ainda.{Cor.RESET}')
      aguardar()
      return
    opcoes = [f'{a.nome} — {a.preco} cobres ({a.bonus_poder_percentual}% de poder)' for a in armas]
    escolha = ler_acao(_titulo(personagem, 'Loja de Equipamentos'), opcoes)
    if escolha is None:
      return
    arma = armas[escolha]
    if arma.nome in personagem.equipamentos_guardados or personagem.arma_equipada == arma.nome:
      escrever(f'{Cor.AMARELO}Você já tem essa arma.{Cor.RESET}')
      aguardar()
      continue
    if _pagar(personagem, arma.preco, escrever):
      personagem.equipamentos_guardados.append(arma.nome)
      escrever(f'{Cor.VERDE}Você comprou {arma.nome}. Equipe-a em Personagem.{Cor.RESET}')
    aguardar()
