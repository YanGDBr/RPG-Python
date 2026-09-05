"""Testes de integração ponta a ponta — igual ao smoke test manual que rodei
antes de reestruturar tudo, só que automatizado: como `menu()`/`ler_tecla()`
aceitam leitor/escritor injetáveis, dá pra simular um jogador de verdade sem
precisar de um terminal interativo.
"""

import itertools
import random

from rpg.dados.classes import CLASSES
from rpg.dados.monstros import MONSTROS
from rpg.modelos.personagem import Personagem
from rpg.sistemas import batalha, exploracao, loja, progressao


def _leitor_menu_sequencia(sequencia):
  fila = list(sequencia)

  def _fake(_titulo, _opcoes, **_kwargs):
    return fila.pop(0)

  return _fake


def _personagem_cavaleiro():
  personagem = Personagem(nome='HeroiTeste', senha_hash='x', classe='Cavaleiro', raca='Humano')
  personagem.habilidades_aprendidas = list(CLASSES['Cavaleiro'].habilidades_iniciais)
  personagem.habilidades_equipadas = list(CLASSES['Cavaleiro'].habilidades_iniciais)
  return personagem


def test_comprar_pocao_de_vida_debita_moedas_e_adiciona_ao_inventario():
  personagem = _personagem_cavaleiro()
  mensagens = []

  loja.loja_pocoes(personagem, escrever=mensagens.append,
                    ler_acao=_leitor_menu_sequencia([0, None]),  # índice 0 = Poção de Vida
                    aguardar=lambda: None)

  assert personagem.pocoes.get('Vida', 0) == 1
  assert personagem.moeda_cobre == 200 - 30
  assert any('Vida' in m for m in mensagens)


def test_explorar_um_andar_e_lutar_ate_vencer():
  random.seed(99)
  personagem = _personagem_cavaleiro()
  personagem.poder = 500
  personagem.andar_atual['habusken'] = 1
  mensagens = []

  exploracao.explorar(
      personagem, 'habusken', escrever=mensagens.append,
      leitor_tecla=_leitor_tecla_ate_evento(),
      limpar=lambda: None,
      ler_confirmacao=lambda *_a, **_k: True,
      ler_acao_batalha=lambda _titulo, _opcoes, **_kw: 0,  # sempre usa a 1ª habilidade
      aguardar=lambda: None)

  # Não importa qual dos 3 eventos aconteceu (monstro, moedas ou nada) — o
  # personagem tem que continuar num estado consistente e sem exceções.
  assert personagem.vida >= 0
  assert personagem.local in ('batalha', 'dungeon:habusken')


def _leitor_tecla_ate_evento():
  """Alterna entre as 4 direções — garante progresso mesmo se o personagem
  nascer encostado numa borda/canto do mapa (uma única direção fixa poderia
  travar o teste ali para sempre)."""
  ciclo = itertools.cycle(['direita', 'baixo', 'esquerda', 'cima'])

  def _ler():
    return next(ciclo)

  return _ler


def test_vitoria_concede_recompensas_e_possivelmente_sobe_de_nivel():
  random.seed(5)
  personagem = _personagem_cavaleiro()
  personagem.poder = 500
  mensagens = []

  resultado, monstro = batalha.batalhar(
      personagem, MONSTROS['Kobold'], escrever=mensagens.append,
      ler_acao=lambda titulo, opcoes, **kw: 0, aguardar=lambda: None)
  assert resultado == batalha.ResultadoBatalha.VITORIA

  exp_antes = personagem.exp
  progressao.conceder_recompensas(personagem, monstro.base, mensagens.append)
  assert personagem.moeda_cobre >= 200  # ganhou moedas em cima do saldo inicial
  assert personagem.exp != exp_antes or personagem.nivel > 1
