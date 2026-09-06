import random

from rpg.config import Cor
from rpg.dados.classes import CLASSES
from rpg.dados.monstros import MONSTROS
from rpg.modelos.monstro import MonstroBatalha
from rpg.modelos.personagem import Personagem
from rpg.sistemas import batalha


def _personagem_cavaleiro():
  p = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  p.habilidades_equipadas = list(CLASSES['Cavaleiro'].habilidades_iniciais)
  return p


def test_multiplicador_elemental_fraqueza_e_resistencia():
  monstro = MonstroBatalha.instanciar(MONSTROS['Slime'])  # fraqueza Fogo, resistência Físico
  assert batalha.multiplicador_elemental('Fogo', monstro) == 1.5
  assert batalha.multiplicador_elemental('Fisico', monstro) == 0.5
  assert batalha.multiplicador_elemental('Eletrico', monstro) == 1.0


def test_calcular_dano_e_sempre_positivo():
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = CLASSES['Cavaleiro'].habilidades_iniciais[0]
  from rpg.dados.habilidades import HABILIDADES
  dano, _critico = batalha.calcular_dano(personagem, HABILIDADES[habilidade], monstro)
  assert dano > 0


def test_fome_critica_reduz_o_dano():
  from rpg.dados.habilidades import HABILIDADES
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = HABILIDADES['Investida']

  personagem_bem_alimentado = _personagem_cavaleiro()
  personagem_bem_alimentado.fome = 10
  random.seed(123)
  dano_normal, _ = batalha.calcular_dano(personagem_bem_alimentado, habilidade, monstro)

  personagem_faminto = _personagem_cavaleiro()
  personagem_faminto.fome = 1
  random.seed(123)
  dano_faminto, _ = batalha.calcular_dano(personagem_faminto, habilidade, monstro)

  assert dano_faminto < dano_normal


def test_batalha_termina_em_vitoria_com_poder_avassalador():
  random.seed(7)
  personagem = _personagem_cavaleiro()
  personagem.poder = 500

  resultado, monstro = batalha.batalhar(
      personagem, MONSTROS['Slime'], escrever=lambda *_a, **_k: None,
      ler_acao=lambda titulo, opcoes, **kw: 0, aguardar=lambda: None)

  assert resultado == batalha.ResultadoBatalha.VITORIA
  assert monstro.vida == 0


def test_batalha_pausa_ao_menos_uma_vez_por_rodada_para_dar_tempo_de_ler():
  """Regressão: as mensagens de dano/efeito apareciam e a tela já limpava
  antes de dar tempo de ler."""
  random.seed(7)
  personagem = _personagem_cavaleiro()
  personagem.poder = 500
  chamadas_aguardar = []

  batalha.batalhar(
      personagem, MONSTROS['Kobold'], escrever=lambda *_a, **_k: None,
      ler_acao=lambda titulo, opcoes, **kw: 0,
      aguardar=lambda: chamadas_aguardar.append(1))

  assert len(chamadas_aguardar) >= 1


def test_mensagem_de_dano_e_colorida_de_vermelho():
  random.seed(1)
  personagem = _personagem_cavaleiro()
  personagem.poder = 10
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  mensagens = []

  from rpg.dados.habilidades import HABILIDADES
  batalha.personagem_ataca(personagem, HABILIDADES['Investida'], monstro, mensagens.append)

  assert any(Cor.VERMELHO in m for m in mensagens)


def test_opcao_de_habilidade_mostra_mana_e_dano_previsto():
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  from rpg.dados.habilidades import HABILIDADES
  descricao = batalha._descricao_habilidade(personagem, HABILIDADES['Investida'], monstro)
  assert 'mana' in descricao
  assert 'dano' in descricao


def test_bonus_percentuais_somam_em_vez_de_multiplicar_em_cadeia():
  """Regressão: cada bônus percentual (poder, arma, Etén...) multiplicava o
  resultado do anterior, então o dano explodia rápido demais quando vários
  bônus se acumulavam. Agora é tudo somado e aplicado de uma vez."""
  from rpg.dados.habilidades import HABILIDADES
  habilidade = HABILIDADES['Investida']  # dano_base 15
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])  # sem fraqueza/resistência física

  personagem = _personagem_cavaleiro()  # raça Humano: +10% de poder; postura padrão 'ofensiva': +10%
  personagem.poder = 10   # 10 * 2% = +20%
  personagem.eten = True  # +15%
  # total esperado: 20% (poder) + 15% (Etén) + 10% (raça Humano) + 10% (postura ofensiva) = +55%
  dano_previsto = batalha.prever_dano(personagem, habilidade, monstro)
  assert dano_previsto == round(15 * 1.55)


def test_chance_de_critico_tem_teto():
  from rpg.dados.habilidades import HABILIDADES
  personagem = _personagem_cavaleiro()
  personagem.sorte = 200  # tentativa de estourar o teto
  chance = batalha.chance_de_critico(personagem, HABILIDADES['Investida'])
  assert chance == 60


def test_queimadura_aplicada_no_monstro_causa_dano_a_cada_rodada():
  """Regressão: a Queimadura era aplicada no monstro mas nunca processada —
  só os efeitos do jogador tinham o tick de dano contínuo."""
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  from rpg.sistemas import efeitos
  efeitos.aplicar_efeito(monstro.efeitos_ativos, 'Queimadura', 2)
  mensagens = []

  vida_antes = monstro.vida
  monstro.vida = efeitos.processar_efeitos_continuos(
      monstro.efeitos_ativos, monstro.vida, mensagens.append, monstro.nome)

  assert monstro.vida < vida_antes
  assert any('Queimadura' in m or 'sofre' in m for m in mensagens)


def test_fraqueza_no_monstro_reduz_o_dano_que_ele_causa():
  from rpg.sistemas import efeitos
  personagem = _personagem_cavaleiro()
  monstro_normal = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  monstro_fraco = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  efeitos.aplicar_efeito(monstro_fraco.efeitos_ativos, 'Fraqueza', 2, valor=50)

  random.seed(1)
  vida_antes = personagem.vida
  batalha.monstro_ataca(personagem, monstro_normal, lambda *_a, **_k: None)
  dano_normal = vida_antes - personagem.vida

  personagem.vida = vida_antes
  random.seed(1)
  batalha.monstro_ataca(personagem, monstro_fraco, lambda *_a, **_k: None)
  dano_fraco = vida_antes - personagem.vida

  assert dano_fraco < dano_normal


def test_fuga_bem_sucedida_termina_em_fuga(monkeypatch):
  personagem = _personagem_cavaleiro()
  monkeypatch.setattr(batalha.random, 'randint', lambda a, b: 1)  # força sucesso na fuga

  resultado, _monstro = batalha.batalhar(
      personagem, MONSTROS['Slime'], escrever=lambda *_a, **_k: None,
      ler_acao=lambda titulo, opcoes, **kw: len(opcoes) - 1,  # sempre "Tentar fugir"
      aguardar=lambda: None)

  assert resultado == batalha.ResultadoBatalha.FUGA


def test_ataque_fisico_detona_queimadura_ativa_no_monstro():
  from rpg.sistemas import efeitos
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  efeitos.aplicar_efeito(monstro.efeitos_ativos, 'Queimadura', 3)
  personagem = _personagem_cavaleiro()
  mensagens = []

  from rpg.dados.habilidades import HABILIDADES
  batalha.personagem_ataca(personagem, HABILIDADES['Investida'], monstro, mensagens.append)

  assert not any(e['nome'] == 'Queimadura' for e in monstro.efeitos_ativos)
  assert any('detona' in m for m in mensagens)


def test_postura_defensiva_reduz_dano_recebido():
  personagem_ofensivo = _personagem_cavaleiro()
  personagem_ofensivo.postura = 'ofensiva'
  personagem_defensivo = _personagem_cavaleiro()
  personagem_defensivo.postura = 'defensiva'

  random.seed(3)
  batalha._receber_ataque_do_monstro(personagem_ofensivo, 100, 'ataque', lambda *_a, **_k: None)
  dano_ofensivo = personagem_ofensivo.vida_maxima - personagem_ofensivo.vida

  personagem_defensivo.vida = personagem_defensivo.vida_maxima
  batalha._receber_ataque_do_monstro(personagem_defensivo, 100, 'ataque', lambda *_a, **_k: None)
  dano_defensivo = personagem_defensivo.vida_maxima - personagem_defensivo.vida

  assert dano_defensivo < dano_ofensivo


def test_furia_do_cavaleiro_aumenta_ao_atacar_e_ao_levar_dano():
  personagem = _personagem_cavaleiro()
  assert personagem.furia_cavaleiro == 0

  from rpg.dados.habilidades import HABILIDADES
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  batalha.personagem_ataca(personagem, HABILIDADES['Investida'], monstro, lambda *_a, **_k: None)
  assert personagem.furia_cavaleiro > 0

  furia_apos_atacar = personagem.furia_cavaleiro
  batalha._receber_ataque_do_monstro(personagem, 10, 'ataque', lambda *_a, **_k: None)
  assert personagem.furia_cavaleiro > furia_apos_atacar


def test_monstro_elite_tem_mais_vida_e_ataca_mais_forte():
  monstro_normal = MonstroBatalha.instanciar(MONSTROS['Kobold'], elite=False)
  monstro_elite = MonstroBatalha.instanciar(MONSTROS['Kobold'], elite=True)
  assert monstro_elite.vida > monstro_normal.vida
  assert 'Elite' in monstro_elite.nome
  assert 'Elite' not in monstro_normal.nome


def test_habilidade_ignora_resistencia_trata_resistencia_como_neutra():
  from rpg.modelos.habilidade import Habilidade
  monstro = MonstroBatalha.instanciar(MONSTROS['Slime'])  # resistente a Fisico (0.5x)
  habilidade_normal = Habilidade(nome='Teste', mana=0, dano_base=100, tipo='ataque', elemento='Fisico')
  habilidade_perfurante = Habilidade(nome='Teste Perfurante', mana=0, dano_base=100, tipo='ataque',
                                       elemento='Fisico', ignora_resistencia=True)
  personagem = _personagem_cavaleiro()

  assert (batalha._multiplicador_elemental_efetivo(personagem, habilidade_normal, monstro) <
          batalha._multiplicador_elemental_efetivo(personagem, habilidade_perfurante, monstro))
  assert batalha._multiplicador_elemental_efetivo(personagem, habilidade_perfurante, monstro) == 1.0


def test_habilidade_sempre_critico_forca_critico():
  from rpg.modelos.habilidade import Habilidade
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = Habilidade(nome='Teste', mana=0, dano_base=10, tipo='ataque', sempre_critico=True)
  _dano, critico = batalha.calcular_dano(personagem, habilidade, monstro)
  assert critico is True


def test_ciclo_elemental_generico_quando_nao_ha_fraqueza_explicita():
  # Fisico > Fogo > Gelo > Eletrico > Agua > Sombrio > Fisico (roda genérica)
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])  # elemento Fisico, sem listas explícitas
  assert batalha.multiplicador_elemental('Sombrio', monstro) > 1.0   # Sombrio é forte contra Fisico
  assert batalha.multiplicador_elemental('Fogo', monstro) < 1.0      # Fisico é forte contra Fogo (o inverso)


def _personagem_mago():
  p = Personagem(nome='teste', classe='Mago', raca='Humano')
  p.habilidades_equipadas = list(CLASSES['Mago'].habilidades_iniciais)
  return p


def test_especializacao_piromante_aumenta_dano_de_fogo():
  from rpg.dados.habilidades import HABILIDADES
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])  # sem fraqueza/resistência a Fogo
  habilidade = HABILIDADES['Chamas']  # elemento Fogo

  sem_especializacao = _personagem_mago()
  com_especializacao = _personagem_mago()
  com_especializacao.especializacao = 'Piromante'

  dano_sem = batalha.prever_dano(sem_especializacao, habilidade, monstro)
  dano_com = batalha.prever_dano(com_especializacao, habilidade, monstro)
  assert dano_com > dano_sem


def test_especializacao_berserker_aumenta_dano_com_vida_baixa():
  from rpg.dados.habilidades import HABILIDADES
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = HABILIDADES['Investida']

  personagem = _personagem_cavaleiro()
  personagem.especializacao = 'Berserker'
  dano_vida_cheia = batalha.prever_dano(personagem, habilidade, monstro)

  personagem.vida = round(personagem.vida_maxima * 0.4)
  dano_vida_baixa = batalha.prever_dano(personagem, habilidade, monstro)
  assert dano_vida_baixa > dano_vida_cheia


def test_especializacao_atirador_de_elite_aumenta_chance_de_critico():
  from rpg.dados.habilidades import HABILIDADES
  personagem = _personagem_cavaleiro()  # classe não importa pro cálculo de crítico
  chance_sem = batalha.chance_de_critico(personagem, HABILIDADES['Investida'])
  personagem.especializacao = 'Atirador de Elite'
  chance_com = batalha.chance_de_critico(personagem, HABILIDADES['Investida'])
  assert chance_com > chance_sem


def test_trocar_postura_nao_gasta_turno():
  """Regressão: trocar de postura era uma ação como qualquer outra e dava a
  vez pro monstro atacar — agora é de graça."""
  personagem = _personagem_cavaleiro()
  personagem.poder = 500  # 1 golpe mata o Kobold
  respostas = iter([3, 0])  # 3 = troca postura (não devia gastar turno), 0 = ataca e vence

  resultado, _monstro = batalha.batalhar(
      personagem, MONSTROS['Kobold'], escrever=lambda *_a, **_k: None,
      ler_acao=lambda *_a, **_k: next(respostas), aguardar=lambda: None)

  assert resultado == batalha.ResultadoBatalha.VITORIA
  assert personagem.vida == personagem.vida_maxima  # nunca levou dano nenhum


def test_chance_de_critico_base_nao_inclui_bonus_de_habilidade():
  personagem = _personagem_cavaleiro()
  personagem.sorte = 5
  from rpg.dados.habilidades import HABILIDADES
  habilidade = HABILIDADES['Meteoro Arcano']  # bonus_critico=15, só pra ter algo != 0
  base = batalha.chance_de_critico_base(personagem)
  com_habilidade = batalha.chance_de_critico(personagem, habilidade)
  assert com_habilidade == base + habilidade.bonus_critico


def test_efeito_de_habilidade_nao_aplica_quando_a_rolagem_falha(monkeypatch):
  from rpg.dados.habilidades import HABILIDADES
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = HABILIDADES['Corte Fatal']  # efeito Sangramento

  monkeypatch.setattr(batalha.random, 'randint', lambda a, b: 100)  # sempre falha a rolagem de efeito
  mensagens = []
  batalha.personagem_ataca(personagem, habilidade, monstro, mensagens.append)

  assert not any(e['nome'] == 'Sangramento' for e in monstro.efeitos_ativos)
  assert any('resistiu' in m for m in mensagens)


def test_efeito_de_habilidade_aplica_quando_a_rolagem_acerta(monkeypatch):
  from rpg.dados.habilidades import HABILIDADES
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = HABILIDADES['Corte Fatal']

  monkeypatch.setattr(batalha.random, 'randint', lambda a, b: 1)  # sempre acerta a rolagem de efeito
  mensagens = []
  batalha.personagem_ataca(personagem, habilidade, monstro, mensagens.append)

  assert any(e['nome'] == 'Sangramento' for e in monstro.efeitos_ativos)


def test_efeito_de_monstro_e_probabilistico_e_avisa_quando_resiste(monkeypatch):
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold Mago'])  # efeito_aplicado='Queimadura'

  monkeypatch.setattr(batalha.random, 'randint', lambda a, b: 100)  # falha esquiva e falha efeito
  mensagens = []
  batalha.monstro_ataca(personagem, monstro, mensagens.append)

  assert personagem.efeitos_ativos == []
  assert any('resistiu' in m for m in mensagens)


def _personagem_arqueiro():
  p = Personagem(nome='teste', classe='Arqueiro', raca='Humano')
  p.habilidades_equipadas = list(CLASSES['Arqueiro'].habilidades_iniciais)
  return p


# ------------------------------------------------------- Grupos de monstros

def test_batalha_com_grupo_devolve_lista_e_termina_quando_todos_morrem():
  personagem = _personagem_cavaleiro()
  personagem.poder = 500
  grupo = [MONSTROS['Slime'], MONSTROS['Slime']]

  resultado, monstros = batalha.batalhar(
      personagem, grupo, escrever=lambda *_a, **_k: None,
      ler_acao=lambda titulo, opcoes, **kw: 0, aguardar=lambda: None)

  assert resultado == batalha.ResultadoBatalha.VITORIA
  assert isinstance(monstros, list)
  assert len(monstros) == 2
  assert all(not m.vivo for m in monstros)


def test_batalha_solo_continua_devolvendo_um_unico_monstro():
  """Backward-compat: passar um MonstroBase avulso (não lista) continua
  devolvendo um MonstroBatalha avulso, não uma lista de 1."""
  personagem = _personagem_cavaleiro()
  personagem.poder = 500

  resultado, monstro = batalha.batalhar(
      personagem, MONSTROS['Kobold'], escrever=lambda *_a, **_k: None,
      ler_acao=lambda titulo, opcoes, **kw: 0, aguardar=lambda: None)

  assert resultado == batalha.ResultadoBatalha.VITORIA
  assert not isinstance(monstro, list)
  assert monstro.base.nome == 'Kobold'


def test_habilidade_em_area_acerta_todos_os_alvos_vivos():
  from rpg.modelos.habilidade import Habilidade
  personagem = _personagem_cavaleiro()
  alvos = [MonstroBatalha.instanciar(MONSTROS['Slime']), MonstroBatalha.instanciar(MONSTROS['Kobold'])]
  habilidade = Habilidade(nome='Teste Área', mana=0, dano_base=1000, tipo='ataque_area')

  batalha.personagem_ataca_alvos(personagem, habilidade, alvos, lambda *_a, **_k: None)

  assert all(not a.vivo for a in alvos)  # 1000 de dano base mata os dois


def test_ataque_normal_em_grupo_mira_so_o_primeiro_alvo_da_lista():
  from rpg.modelos.habilidade import Habilidade
  personagem = _personagem_cavaleiro()
  alvo_1 = MonstroBatalha.instanciar(MONSTROS['Slime'])
  alvo_2 = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = Habilidade(nome='Teste', mana=0, dano_base=1000, tipo='ataque')

  batalha.personagem_ataca_alvos(personagem, habilidade, [alvo_1, alvo_2], lambda *_a, **_k: None)

  assert not alvo_1.vivo
  assert alvo_2.vivo  # não foi tocado


# ------------------------------------------------------------------- Foco

def test_foco_do_arqueiro_aumenta_ao_atacar():
  personagem = _personagem_arqueiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  assert personagem.foco_arqueiro == 0

  from rpg.dados.habilidades import HABILIDADES
  batalha.personagem_ataca(personagem, HABILIDADES['Flecha Rápida'], monstro, lambda *_a, **_k: None)

  assert personagem.foco_arqueiro > 0


def test_foco_nao_aumenta_pra_outras_classes():
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  from rpg.dados.habilidades import HABILIDADES
  batalha.personagem_ataca(personagem, HABILIDADES['Investida'], monstro, lambda *_a, **_k: None)
  assert personagem.foco_arqueiro == 0


# --------------------------------------------------------------- Marcado

def test_marcado_aumenta_o_dano_recebido_pelo_alvo():
  from rpg.modelos.habilidade import Habilidade
  personagem = _personagem_arqueiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade_neutra = Habilidade(nome='Teste', mana=0, dano_base=100, tipo='ataque', elemento='Fisico')

  from rpg.sistemas import efeitos
  dano_sem_marca = batalha.prever_dano(personagem, habilidade_neutra, monstro)
  efeitos.aplicar_efeito(monstro.efeitos_ativos, 'Marcado', 3, 25)
  dano_com_marca = batalha.prever_dano(personagem, habilidade_neutra, monstro)

  assert dano_com_marca > dano_sem_marca


# ------------------------------------------------------- Flecha elemental

def test_arqueiro_pode_trocar_elemento_da_flecha_de_graca():
  from rpg.modelos.habilidade import Habilidade
  personagem = _personagem_arqueiro()
  habilidade_generica = Habilidade(nome='Teste', mana=0, dano_base=10, tipo='ataque', elemento='Fisico')

  assert batalha._elemento_efetivo(personagem, habilidade_generica) == 'Fisico'
  personagem.elemento_flecha_atual = 'Gelo'
  assert batalha._elemento_efetivo(personagem, habilidade_generica) == 'Gelo'


def test_troca_de_elemento_da_flecha_nao_gasta_turno():
  personagem = _personagem_arqueiro()
  personagem.poder = 500
  # labels: [0,1,2]=habilidades, 3=postura, 4=trocar flecha, depois ataca e vence
  respostas = iter([4, 0])

  resultado, _monstro = batalha.batalhar(
      personagem, MONSTROS['Kobold'], escrever=lambda *_a, **_k: None,
      ler_acao=lambda *_a, **_k: next(respostas), aguardar=lambda: None)

  assert resultado == batalha.ResultadoBatalha.VITORIA
  assert personagem.vida == personagem.vida_maxima  # o monstro nunca chegou a atacar
  assert personagem.elemento_flecha_atual != 'Fisico'


def test_habilidade_de_elemento_fixo_nao_e_afetada_pela_troca():
  from rpg.modelos.habilidade import Habilidade
  personagem = _personagem_arqueiro()
  personagem.elemento_flecha_atual = 'Gelo'
  habilidade_com_elemento_proprio = Habilidade(nome='Teste', mana=0, dano_base=10, tipo='ataque', elemento='Sombrio')
  assert batalha._elemento_efetivo(personagem, habilidade_com_elemento_proprio) == 'Sombrio'


# ------------------------------------------------------ Ressonância Arcana

def test_ressonancia_arcana_sobe_ao_variar_elemento():
  personagem = _personagem_mago()
  from rpg.dados.habilidades import HABILIDADES
  batalha._atualizar_ressonancia_arcana(personagem, HABILIDADES['Chamas'])  # Fogo
  assert personagem.ressonancia_arcana == 1
  batalha._atualizar_ressonancia_arcana(personagem, HABILIDADES['Raio'])  # Elétrico
  assert personagem.ressonancia_arcana == 2


def test_ressonancia_arcana_zera_ao_repetir_elemento():
  personagem = _personagem_mago()
  from rpg.dados.habilidades import HABILIDADES
  batalha._atualizar_ressonancia_arcana(personagem, HABILIDADES['Chamas'])  # Fogo
  batalha._atualizar_ressonancia_arcana(personagem, HABILIDADES['Chamas'])  # Fogo de novo
  assert personagem.ressonancia_arcana == 0


def test_ressonancia_arcana_aumenta_o_dano_do_mago():
  personagem = _personagem_mago()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  from rpg.dados.habilidades import HABILIDADES
  habilidade = HABILIDADES['Missil Mágico']

  dano_sem_stacks = batalha.prever_dano(personagem, habilidade, monstro)
  personagem.ressonancia_arcana = 3
  dano_com_stacks = batalha.prever_dano(personagem, habilidade, monstro)

  assert dano_com_stacks > dano_sem_stacks


# ------------------------------------------------------ Item por turno

def test_so_pode_usar_um_item_por_turno_sem_gastar_turno(monkeypatch):
  personagem = _personagem_cavaleiro()
  personagem.pocoes['Vida'] = 5
  personagem.vida = 1  # sobrevive fácil, mesmo sem curar
  # índices do menu principal: [0,1,2]=habilidades, 3=postura, 4=itens, 5=pular
  # usa item (cura, sub-menu escolhe a poção no índice 0), tenta usar de novo
  # (bloqueado, de graça, sem sub-menu), pula a vez.
  respostas = iter([4, 0, 4, 5])
  chamadas_monstro_ataca = []
  original = batalha.monstro_ataca
  monkeypatch.setattr(batalha, 'monstro_ataca',
                      lambda *a, **k: (chamadas_monstro_ataca.append(1), original(*a, **k))[1])

  try:
    batalha.batalhar(personagem, MONSTROS['Kobold'], escrever=lambda *_a, **_k: None,
                      ler_acao=lambda *_a, **_k: next(respostas), aguardar=lambda: None)
  except StopIteration:
    pass  # só nos importa o que aconteceu no primeiro turno, scriptado acima

  # só "pular" (a 4ª resposta) devia ter passado a vez pro monstro — as duas
  # tentativas de item (uma bem-sucedida, uma bloqueada) não contam turno.
  assert len(chamadas_monstro_ataca) == 1


# --------------------------------------------------------- Atordoamento

def test_bater_na_fraqueza_repetidamente_atordoa_o_monstro():
  from rpg.config import ATORDOAMENTO_GANHO_POR_ACERTO_FRACO, ATORDOAMENTO_LIMIAR
  from rpg.modelos.habilidade import Habilidade
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Slime'])  # fraqueza Fogo
  # habilidade sintética de Fogo, pra não depender de qual está equipada
  habilidade_fogo = Habilidade(nome='Teste Fogo', mana=0, dano_base=1, tipo='ataque', elemento='Fogo')

  golpes_necessarios = -(-ATORDOAMENTO_LIMIAR // ATORDOAMENTO_GANHO_POR_ACERTO_FRACO)
  for _ in range(golpes_necessarios):
    if not monstro.vivo:
      break
    batalha.personagem_ataca(personagem, habilidade_fogo, monstro, lambda *_a, **_k: None)

  assert any(e['nome'] == 'Atordoado' for e in monstro.efeitos_ativos)


def test_monstro_atordoado_perde_a_vez():
  from rpg.sistemas import efeitos
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  efeitos.aplicar_efeito(monstro.efeitos_ativos, 'Atordoado', 1)
  vida_antes = personagem.vida

  fugiu = batalha.monstro_ataca(personagem, monstro, lambda *_a, **_k: None)

  assert fugiu is False
  assert personagem.vida == vida_antes  # não atacou


# -------------------------------------------------------- Fase de fúria

def test_fase_furiosa_ativa_a_meia_vida_e_aumenta_o_dano(monkeypatch):
  from rpg.modelos.monstro import MonstroBase
  base = MonstroBase(nome='Chefe Teste', vida_maxima=100, ataque_min=50, ataque_max=50,
                      nivel=10, chefe=True, tem_fase_furiosa=True)
  monstro = MonstroBatalha.instanciar(base)
  personagem = _personagem_cavaleiro()

  monstro.vida = 50  # exatamente na metade
  batalha._verificar_fase_furiosa(monstro, lambda *_a, **_k: None)
  assert monstro.fase_furiosa_ativa is True

  monkeypatch.setattr(batalha.random, 'randint', lambda a, b: 50)  # sem crítico/esquiva
  vida_antes = personagem.vida
  batalha.monstro_ataca(personagem, monstro, lambda *_a, **_k: None)
  dano_com_fase = vida_antes - personagem.vida

  monstro2 = MonstroBatalha.instanciar(base)
  personagem2 = _personagem_cavaleiro()
  batalha.monstro_ataca(personagem2, monstro2, lambda *_a, **_k: None)
  dano_sem_fase = personagem2.vida_maxima - personagem2.vida

  assert dano_com_fase > dano_sem_fase


# ------------------------------------------------------- Canalização

def test_minigame_canalizacao_conta_acertos_na_sequencia(monkeypatch):
  sequencia_fixa = iter('ABCD')
  monkeypatch.setattr(batalha.random, 'choice', lambda _seq: next(sequencia_fixa))
  acertos, total = batalha._minigame_canalizacao(
      escrever=lambda *_a, **_k: None, limpar=lambda: None, esperar=lambda _s: None,
      entrada_texto=lambda _p: 'ABCD')
  assert acertos == total == 4


def test_habilidade_canalizavel_aplica_bonus_pendente_no_proximo_golpe(monkeypatch):
  from rpg.modelos.habilidade import Habilidade
  personagem = _personagem_cavaleiro()
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  habilidade = Habilidade(nome='Teste', mana=0, dano_base=100, tipo='ataque')

  dano_normal = batalha.prever_dano(personagem, habilidade, monstro)
  personagem.bonus_canalizacao_pendente = 60
  dano_canalizado = batalha.prever_dano(personagem, habilidade, monstro)
  assert dano_canalizado > dano_normal

  # some sozinho depois do golpe
  batalha.personagem_ataca(personagem, habilidade, monstro, lambda *_a, **_k: None)
  assert personagem.bonus_canalizacao_pendente == 0


# ---------------------------------------------------- Novos acessórios

def test_resistencia_efeito_reduz_chance_de_grudar_status(monkeypatch):
  assert batalha._efeito_grudou(bonus_resistencia=100) is False  # sempre resiste
  monkeypatch.setattr(batalha.random, 'randint', lambda a, b: 1)
  assert batalha._efeito_grudou(bonus_resistencia=0) is True


def test_vida_ao_matar_cura_personagem_ao_finalizar_o_alvo(monkeypatch):
  from rpg.dados.itens import Acessorio
  personagem = _personagem_cavaleiro()
  personagem.vida = 1
  personagem.acessorios_equipados = ['Relíquia de Teste']
  monkeypatch.setattr('rpg.sistemas.equipamento.ACESSORIOS', {
    'Relíquia de Teste': Acessorio('Relíquia de Teste', 'teste', 'vida_ao_matar', 50),
  })
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  monstro.vida = 1  # qualquer golpe mata
  from rpg.modelos.habilidade import Habilidade
  habilidade = Habilidade(nome='Teste', mana=0, dano_base=100, tipo='ataque')

  batalha.personagem_ataca(personagem, habilidade, monstro, lambda *_a, **_k: None)

  assert personagem.vida > 1


def test_contra_ataque_causa_dano_ao_esquivar(monkeypatch):
  from rpg.dados.itens import Acessorio
  personagem = _personagem_cavaleiro()
  personagem.acessorios_equipados = ['Espinho de Teste']
  monkeypatch.setattr('rpg.sistemas.equipamento.ACESSORIOS', {
    'Espinho de Teste': Acessorio('Espinho de Teste', 'teste', 'contra_ataque', 100),
  })
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])
  vida_antes = monstro.vida
  monkeypatch.setattr(batalha.random, 'randint', lambda a, b: 1)  # esquiva sempre, contra-ataca sempre

  batalha.monstro_ataca(personagem, monstro, lambda *_a, **_k: None)

  assert monstro.vida < vida_antes


def test_furia_extra_do_acessorio_soma_ao_ganho_normal(monkeypatch):
  from rpg.config import FURIA_GANHA_AO_ATACAR
  from rpg.dados.habilidades import HABILIDADES
  from rpg.dados.itens import Acessorio
  personagem = _personagem_cavaleiro()
  personagem.acessorios_equipados = ['Bracelete de Teste']
  monkeypatch.setattr('rpg.sistemas.equipamento.ACESSORIOS', {
    'Bracelete de Teste': Acessorio('Bracelete de Teste', 'teste', 'furia_extra', 20),
  })
  monstro = MonstroBatalha.instanciar(MONSTROS['Kobold'])

  batalha.personagem_ataca(personagem, HABILIDADES['Investida'], monstro, lambda *_a, **_k: None)

  assert personagem.furia_cavaleiro >= FURIA_GANHA_AO_ATACAR + 20
