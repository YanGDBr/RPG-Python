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
  personagem = Personagem(nome='teste', senha_hash='x', classe='Mago', raca='Humano')
  personagem.nivel = 1
  personagem.moeda_cobre = 10_000
  mensagens = []

  loja.loja_equipamentos(personagem, escrever=mensagens.append,
                          ler_acao=lambda *_a, **_k: None, aguardar=lambda: None)

  assert 'Cajado de Madeira Velha' not in ' '.join(mensagens)
  assert personagem.equipamentos_guardados == []
