"""Testes do Ancião de Habusken: pedido do usuário pra ele ter múltiplos
diálogos em vez de sempre repetir o mesmo bloco de texto fixo."""

from rpg.dados.npcs import NPCS


def _personagem():
  class _Fake:
    chefes_derrotados = []
    cratera_vhalos_liberado = False
  return _Fake()


def test_anciao_tem_um_bom_leque_de_falas_aleatorias():
  from rpg.dados.npcs import _ANCIAO_LINHAS_ALEATORIAS
  assert len(_ANCIAO_LINHAS_ALEATORIAS) >= 10


def test_anciao_varia_as_falas_entre_visitas():
  """Não é garantido que duas chamadas sejam diferentes por puro acaso, mas
  rodando várias vezes é praticamente certo ver pelo menos duas
  combinações distintas — prova que não é mais sempre o mesmo bloco fixo."""
  personagem = _personagem()
  combinacoes = {tuple(NPCS['anciao_habusken'].falas(personagem)) for _ in range(30)}
  assert len(combinacoes) > 1


def test_anciao_sempre_mostra_falas_de_marco_quando_aplicaveis():
  personagem = _personagem()
  personagem.chefes_derrotados = ['Dragão Ancião de Habusken']

  for _ in range(10):
    falas = NPCS['anciao_habusken'].falas(personagem)
    assert any('Dragão Ancião' in f for f in falas)
