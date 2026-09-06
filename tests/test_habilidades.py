"""Invariantes do catálogo de habilidades: toda entrada referenciada existe
de verdade, o preço/nível sobe junto com o poder, e as novas mecânicas
(Foco, Fúria, área, canalização, Marcado) estão realmente ligadas em pelo
menos uma habilidade de cada classe onde fazem sentido."""

from rpg.dados.habilidades import HABILIDADES, HABILIDADES_DESBLOQUEAVEIS, HABILIDADES_INICIAIS


def test_toda_habilidade_desbloqueavel_existe_no_catalogo():
  for classe, nomes in HABILIDADES_DESBLOQUEAVEIS.items():
    for nome in nomes:
      assert nome in HABILIDADES, f'{nome} ({classe}) não está em HABILIDADES'


def test_toda_habilidade_inicial_existe_no_catalogo():
  for classe, nomes in HABILIDADES_INICIAIS.items():
    for nome in nomes:
      assert nome in HABILIDADES, f'{nome} ({classe}) não está em HABILIDADES'


def test_desbloqueaveis_estao_em_ordem_crescente_de_nivel():
  for classe, nomes in HABILIDADES_DESBLOQUEAVEIS.items():
    niveis = [HABILIDADES[nome].nivel_minimo for nome in nomes]
    assert niveis == sorted(niveis), f'{classe} não está em ordem crescente de nível'


def test_preco_sobe_junto_com_o_nivel_minimo():
  for classe, nomes in HABILIDADES_DESBLOQUEAVEIS.items():
    precos = [HABILIDADES[nome].preco for nome in nomes]
    assert precos == sorted(precos), f'{classe}: preço deveria subir junto com o nível'


def test_cada_classe_tem_pelo_menos_uma_habilidade_de_area():
  for classe, nomes in HABILIDADES_DESBLOQUEAVEIS.items():
    assert any(HABILIDADES[nome].tipo == 'ataque_area' for nome in nomes), \
        f'{classe} não tem nenhuma habilidade em área'


def test_cada_classe_tem_pelo_menos_uma_habilidade_canalizavel():
  for classe, nomes in HABILIDADES_DESBLOQUEAVEIS.items():
    assert any(HABILIDADES[nome].canalizavel for nome in nomes), \
        f'{classe} não tem nenhuma habilidade canalizável'


def test_cavaleiro_tem_habilidades_que_gastam_furia_alem_da_especializacao():
  nomes_furia = [n for n in HABILIDADES_DESBLOQUEAVEIS['Cavaleiro'] if HABILIDADES[n].custo_furia > 0]
  assert len(nomes_furia) >= 2


def test_arqueiro_tem_habilidades_que_gastam_foco():
  nomes_foco = [n for n in HABILIDADES_DESBLOQUEAVEIS['Arqueiro'] if HABILIDADES[n].custo_foco > 0]
  assert len(nomes_foco) >= 2


def test_arqueiro_tem_marcar_alvo_disponivel_cedo():
  marcar = HABILIDADES['Marcar Alvo']
  assert marcar.efeito == 'Marcado'
  assert marcar.nivel_minimo <= 5


def test_mago_tem_pelo_menos_uma_habilidade_de_cada_elemento_do_ciclo():
  from rpg.config import CICLO_ELEMENTAL
  nomes_mago = HABILIDADES_INICIAIS['Mago'] + HABILIDADES_DESBLOQUEAVEIS['Mago']
  elementos_disponiveis = {HABILIDADES[n].elemento for n in nomes_mago}
  faltando = set(CICLO_ELEMENTAL) - elementos_disponiveis
  assert not faltando, f'Mago sem nenhuma habilidade destes elementos: {faltando}'


def test_nao_ha_nomes_de_habilidade_duplicados_entre_categorias():
  todos = (list(HABILIDADES_INICIAIS['Mago']) + list(HABILIDADES_INICIAIS['Cavaleiro'])
           + list(HABILIDADES_INICIAIS['Arqueiro']) + list(HABILIDADES_DESBLOQUEAVEIS['Mago'])
           + list(HABILIDADES_DESBLOQUEAVEIS['Cavaleiro']) + list(HABILIDADES_DESBLOQUEAVEIS['Arqueiro']))
  assert len(todos) == len(set(todos))
