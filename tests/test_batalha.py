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

  assert (batalha._multiplicador_elemental_efetivo(habilidade_normal, monstro) <
          batalha._multiplicador_elemental_efetivo(habilidade_perfurante, monstro))
  assert batalha._multiplicador_elemental_efetivo(habilidade_perfurante, monstro) == 1.0


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


def test_autobatalha_ataca_sozinho_por_varios_turnos_sem_pedir_nova_acao():
  """A autobatalha deve resolver vários turnos usando sempre a melhor
  habilidade disponível, sem voltar a perguntar a ação a cada turno."""
  random.seed(2)
  personagem = _personagem_cavaleiro()
  chamadas_menu = []

  def _fake_menu(_titulo, opcoes, **_kw):
    chamadas_menu.append(1)
    return next(i for i, label in enumerate(opcoes) if 'Autobatalha' in label)

  resultado, monstro = batalha.batalhar(
      personagem, MONSTROS['Kobold'], escrever=lambda *_a, **_k: None,
      ler_acao=_fake_menu, aguardar=lambda: None)

  assert resultado == batalha.ResultadoBatalha.VITORIA
  assert len(chamadas_menu) == 1   # só ativou a autobatalha uma vez — o resto foi sozinho


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
