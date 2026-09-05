"""Testes de regressão pros bônus de acessório com múltiplos slots — antes só
existia 1 slot (`acessorio_equipado`), agora é uma lista (`acessorios_equipados`)
e os bônus aditivos precisam somar entre os equipados, não só olhar um."""

from rpg.modelos.personagem import Personagem
from rpg.sistemas import equipamento


def _personagem():
  return Personagem(nome='teste', classe='Cavaleiro', raca='Humano')


def test_sem_acessorio_bonus_e_zero():
  personagem = _personagem()
  assert equipamento.chance_critico_extra_acessorio(personagem) == 0
  assert equipamento.reducao_dano_acessorio(personagem) == 0
  assert equipamento.resolver_acessorios(personagem) == []


def test_um_acessorio_aplica_seu_bonus():
  personagem = _personagem()
  personagem.acessorios_equipados = ['Bracelete da Sorte']  # critico, valor 10
  assert equipamento.chance_critico_extra_acessorio(personagem) == 10


def test_dois_acessorios_do_mesmo_tipo_somam(monkeypatch):
  from rpg.dados.itens import Acessorio
  personagem = _personagem()
  personagem.acessorios_equipados = ['A', 'B']
  monkeypatch.setattr(equipamento, 'ACESSORIOS', {
    'A': Acessorio('A', 'teste', 'critico', 10),
    'B': Acessorio('B', 'teste', 'critico', 15),
  })
  assert equipamento.chance_critico_extra_acessorio(personagem) == 25


def test_bonus_boss_usa_o_melhor_divisor_nao_soma(monkeypatch):
  """O efeito 'boss' guarda um divisor (menor = mais frequente) — somar dois
  divisores não faria sentido nenhum, então usa o menor entre os equipados."""
  from rpg.dados.itens import Acessorio
  personagem = _personagem()
  personagem.acessorios_equipados = ['A', 'B']
  monkeypatch.setattr(equipamento, 'ACESSORIOS', {
    'A': Acessorio('A', 'teste', 'boss', 5),
    'B': Acessorio('B', 'teste', 'boss', 3),
  })
  assert equipamento.chance_boss_extra_acessorio(personagem) == 3


def test_vida_maxima_efetiva_soma_bonus_fixo_de_varios_acessorios(monkeypatch):
  from rpg.dados.itens import Acessorio
  personagem = _personagem()
  personagem.acessorios_equipados = ['A', 'B']
  monkeypatch.setattr(equipamento, 'ACESSORIOS', {
    'A': Acessorio('A', 'teste', 'mana_vida', 20),
    'B': Acessorio('B', 'teste', 'mana_vida', 30),
  })
  vida_base = personagem.vida_maxima
  assert equipamento.vida_maxima_efetiva(personagem) == vida_base + 50


def test_efeitos_iniciais_de_batalha_devolve_um_por_acessorio_equipado(monkeypatch):
  from rpg.dados.itens import Acessorio
  personagem = _personagem()
  personagem.acessorios_equipados = ['Anel de Fogo', 'Anel de Fogo 2']
  monkeypatch.setattr(equipamento, 'ACESSORIOS', {
    'Anel de Fogo': Acessorio('Anel de Fogo', 'teste', 'queimadura_inicial', 3),
    'Anel de Fogo 2': Acessorio('Anel de Fogo 2', 'teste', 'queimadura_inicial', 2),
  })
  efeitos = equipamento.efeitos_iniciais_de_batalha_acessorios(personagem)
  assert efeitos == [('Queimadura', 3), ('Queimadura', 2)]


def test_resolver_acessorios_ignora_nome_nao_encontrado():
  personagem = _personagem()
  personagem.acessorios_equipados = ['Isso não existe']
  assert equipamento.resolver_acessorios(personagem) == []
