from rpg.dados.lojas import armas_disponiveis_para_classe
from rpg.modelos.personagem import Personagem
from rpg.sistemas import loja


def test_arma_tier_2_exige_nivel_minimo():
  """Regressão: era possível comprar a arma de 20% de poder logo no nível 1,
  o que deixava o personagem forte demais cedo demais."""
  armas_mago = armas_disponiveis_para_classe('Mago')
  cajado_madeira = next(a for a in armas_mago if a.nome == 'Cajado de Madeira Velha')
  assert cajado_madeira.nivel_minimo > 1


def test_loja_equipamentos_esconde_armas_acima_do_nivel(monkeypatch):
  personagem = Personagem(nome='teste', classe='Mago', raca='Humano')
  personagem.nivel = 1
  personagem.moeda_cobre = 10_000
  mensagens = []

  loja.loja_equipamentos(personagem, escrever=mensagens.append,
                          ler_acao=lambda *_a, **_k: None, aguardar=lambda: None)

  assert 'Cajado de Madeira Velha' not in ' '.join(mensagens)
  assert personagem.equipamentos_guardados == []


def test_ofertas_do_dia_sao_deterministicas_para_o_mesmo_dia():
  assert loja._ofertas_do_dia() == loja._ofertas_do_dia()


def test_loja_acessorios_vende_so_acessorios():
  """A loja de itens/acessórios/comida era uma tela só — foi separada em 3
  categorias (Acessórios, Itens, Comida) a pedido do usuário."""
  from rpg.dados.lojas import CATALOGO_ACESSORIOS
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.moeda_cobre = 10_000

  respostas_menu = iter([0, None])
  loja.loja_acessorios(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _t, _o, **_k: next(respostas_menu), aguardar=lambda: None)

  assert personagem.acessorios_guardados == [CATALOGO_ACESSORIOS[0].nome]


def test_loja_itens_consumiveis_vende_so_itens():
  from rpg.dados.lojas import CATALOGO_ITENS_CONSUMIVEIS
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.moeda_cobre = 10_000

  respostas_menu = iter([0, None])
  loja.loja_itens_consumiveis(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _t, _o, **_k: next(respostas_menu), aguardar=lambda: None)

  assert personagem.inventario.get(CATALOGO_ITENS_CONSUMIVEIS[0].nome, 0) == 1


def test_loja_comidas_vende_so_comida():
  from rpg.dados.lojas import COMIDAS_VENDIDAS
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.moeda_cobre = 10_000
  antes = personagem.comidas.get(COMIDAS_VENDIDAS[0], 0)

  respostas_menu = iter([0, None])
  loja.loja_comidas(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _t, _o, **_k: next(respostas_menu), aguardar=lambda: None)

  assert personagem.comidas.get(COMIDAS_VENDIDAS[0], 0) == antes + 1


def test_ofertas_do_dia_cobra_preco_com_desconto():
  personagem = Personagem(nome='teste', classe='Mago', raca='Humano')
  personagem.moeda_cobre = 10_000
  saldo_antes = personagem.moeda_cobre

  respostas_menu = iter([0, None])

  loja.loja_ofertas_do_dia(
      personagem, escrever=lambda *_a, **_k: None,
      ler_acao=lambda _titulo, _opcoes, **_kw: next(respostas_menu),
      aguardar=lambda: None)

  gasto = saldo_antes - personagem.moeda_cobre
  item = loja._ofertas_do_dia()[0]
  assert gasto == loja._preco_com_desconto(item.preco)
  assert gasto < item.preco
