import pytest

from rpg import jogo
from rpg.dados.classes import CLASSES
from rpg.modelos.personagem import Personagem


def _fake_menu_sequencia(sequencia):
  fila = list(sequencia)

  def _fake(_titulo, _opcoes, **_kwargs):
    return fila.pop(0)

  return _fake


def test_criar_personagem_define_raca_classe_e_habilidades(monkeypatch):
  monkeypatch.setattr(jogo, 'pedir_texto', lambda *_a, **_k: 'Fulano')
  # 1ª chamada de menu = raça (índice 1 = Humano), 2ª = classe (índice 1 = Cavaleiro)
  monkeypatch.setattr(jogo, 'menu_padrao', _fake_menu_sequencia([1, 1]))
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)

  personagem = jogo._criar_personagem()

  assert personagem.nome == 'Fulano'
  assert personagem.raca == 'Humano'
  assert personagem.classe == 'Cavaleiro'
  assert personagem.habilidades_equipadas == CLASSES['Cavaleiro'].habilidades_iniciais
  assert personagem.habilidades_aprendidas == CLASSES['Cavaleiro'].habilidades_iniciais
  assert personagem.esquiva == 5  # Humano não bonifica esquiva (só Fada bonifica)
  assert personagem.local == 'vila'


def test_criar_personagem_fada_ganha_bonus_de_esquiva(monkeypatch):
  monkeypatch.setattr(jogo, 'pedir_texto', lambda *_a, **_k: 'Fadinha')
  monkeypatch.setattr(jogo, 'menu_padrao', _fake_menu_sequencia([0, 0]))  # Fada, Mago
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)

  personagem = jogo._criar_personagem()

  assert personagem.raca == 'Fada'
  assert personagem.esquiva == 5 + 6  # base + bônus da raça Fada


def test_caixa_slot_vazio_nao_quebra_com_personagem_none():
  caixa = jogo._caixa_slot(0, None)
  assert 'SLOT 1' in caixa
  assert 'vazio' in caixa


def test_caixa_slot_preenchido_mostra_nome_classe_e_nivel():
  personagem = Personagem(nome='Herói', classe='Cavaleiro', raca='Humano')
  personagem.nivel = 7
  caixa = jogo._caixa_slot(1, personagem)
  assert 'Herói' in caixa
  assert 'Cavaleiro' in caixa
  assert 'Nv.7' in caixa


def test_autosalvar_nao_salva_na_primeira_chamada(monkeypatch):
  """A primeira checagem só marca o início da contagem — não faz sentido
  salvar no exato instante em que o jogador entrou na tela."""
  jogo._estado_autosave['ultimo'] = None
  chamadas_salvar = []
  monkeypatch.setattr(jogo, 'salvar_slots', lambda slots: chamadas_salvar.append(slots))
  monkeypatch.setattr(jogo.time, 'monotonic', lambda: 1000.0)

  jogo._talvez_autosalvar(Personagem(nome='teste'), slots=['s'])

  assert chamadas_salvar == []


def test_autosalvar_dispara_apos_o_intervalo_configurado(monkeypatch):
  jogo._estado_autosave['ultimo'] = None
  chamadas_salvar = []
  monkeypatch.setattr(jogo, 'salvar_slots', lambda slots: chamadas_salvar.append(slots))
  relogio = {'agora': 1000.0}
  monkeypatch.setattr(jogo.time, 'monotonic', lambda: relogio['agora'])

  personagem = Personagem(nome='teste')
  jogo._talvez_autosalvar(personagem, slots=['s'])  # marca o início
  assert chamadas_salvar == []

  relogio['agora'] += jogo.INTERVALO_AUTOSAVE_SEGUNDOS - 1
  jogo._talvez_autosalvar(personagem, slots=['s'])  # ainda não passou o suficiente
  assert chamadas_salvar == []

  relogio['agora'] += 2
  jogo._talvez_autosalvar(personagem, slots=['s'])  # agora sim
  assert chamadas_salvar == [['s']]


def test_exportar_backup_ui_mostra_local_quando_ha_save(monkeypatch, tmp_path):
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)
  destino = tmp_path / 'backup_saves_20260101_000000.json'
  monkeypatch.setattr(jogo.persistencia, 'exportar_backup', lambda: destino)
  mensagens = []
  monkeypatch.setattr('builtins.print', lambda *args, **_k: mensagens.append(' '.join(str(a) for a in args)))
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')

  jogo._exportar_backup_ui()

  assert any(str(destino) in m for m in mensagens)


def test_exportar_backup_ui_sem_save_mostra_erro(monkeypatch):
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)

  def _levanta():
    raise FileNotFoundError('Nenhum save encontrado ainda.')

  monkeypatch.setattr(jogo.persistencia, 'exportar_backup', _levanta)
  mensagens = []
  monkeypatch.setattr('builtins.print', lambda *args, **_k: mensagens.append(' '.join(str(a) for a in args)))
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')

  jogo._exportar_backup_ui()  # não deve levantar — o erro é só mostrado

  assert any('Nenhum save encontrado' in m for m in mensagens)


def test_importar_backup_ui_sem_backups_devolve_slots_inalterados(monkeypatch):
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)
  monkeypatch.setattr(jogo.persistencia, 'listar_backups', lambda: [])
  monkeypatch.setattr('builtins.print', lambda *_a, **_k: None)
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')

  slots_originais = [None, None, None]
  resultado = jogo._importar_backup_ui(slots_originais)

  assert resultado is slots_originais


def test_importar_backup_ui_confirma_e_recarrega_slots(monkeypatch, tmp_path):
  backup_falso = tmp_path / 'backup_saves_20260101_000000.json'
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)
  monkeypatch.setattr(jogo, 'menu_padrao', lambda *_a, **_k: 0)  # escolhe o único backup listado
  monkeypatch.setattr(jogo, 'perguntar_sim_nao', lambda *_a, **_k: True)
  monkeypatch.setattr(jogo.persistencia, 'listar_backups', lambda: [backup_falso])
  chamadas_importar = []
  monkeypatch.setattr(jogo.persistencia, 'importar_backup', lambda origem: chamadas_importar.append(origem))
  slots_novos = [Personagem(nome='Restaurado'), None, None]
  monkeypatch.setattr(jogo.persistencia, 'carregar_slots', lambda: slots_novos)
  monkeypatch.setattr('builtins.print', lambda *_a, **_k: None)
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')

  resultado = jogo._importar_backup_ui([None, None, None])

  assert chamadas_importar == [backup_falso]
  assert resultado is slots_novos


def test_dungeon_e_vila_usam_o_inventario_de_cidade(monkeypatch):
  """A tela de inventário virou `cidade.tela_inventario` (ganhou materiais e
  comidas, e passou a aparecer também na vila, não só dentro da dungeon)."""
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  chamadas = []
  monkeypatch.setattr(jogo.cidade, 'tela_inventario', lambda *_a, **_k: chamadas.append(1))

  jogo._executar_acao_vila('Inventário', personagem, slots=[None, None, None])

  assert chamadas == [1]


def test_entrar_cratera_bloqueado_antes_de_liberar():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  mensagens = []

  resultado = jogo._entrar_cratera_callback(
      personagem, mensagens.append, lambda: None, lambda: None)

  assert resultado is None
  assert any('não ir' in m for m in mensagens)


def test_entrar_cratera_liberada_retorna_sinal_de_viagem():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.cratera_vhalos_liberado = True
  personagem.adicionar_item_especial('Selo de Vethgard')

  resultado = jogo._entrar_cratera_callback(
      personagem, lambda *_a, **_k: None, lambda: None, lambda: None)

  assert resultado == 'cratera'


def test_entrar_cratera_sem_selo_de_vethgard_ainda_bloqueia():
  """Regressão: o requisito de verdade pra passar é o documento de
  identidade, não só a flag — pediu-se um item físico como "identidade"."""
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.cratera_vhalos_liberado = True  # flag ligada, mas sem o selo

  resultado = jogo._entrar_cratera_callback(
      personagem, lambda *_a, **_k: None, lambda: None, lambda: None)

  assert resultado is None


def test_entrar_vethgard_sem_selo_de_habusken_bloqueia():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  mensagens = []

  resultado = jogo._entrar_vethgard_callback(
      personagem, mensagens.append, lambda: None, lambda: None)

  assert resultado is None
  assert any('Selo de Habusken' in m for m in mensagens)


def test_entrar_vethgard_com_selo_de_habusken_libera_passagem():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.adicionar_item_especial('Selo de Habusken')

  resultado = jogo._entrar_vethgard_callback(
      personagem, lambda *_a, **_k: None, lambda: None, lambda: None)

  assert resultado == 'vethgard'


def test_entrar_torre_arcana_bloqueada_sem_liberar():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  mensagens = []

  resultado = jogo._entrar_torre_arcana_callback(
      personagem, mensagens.append, lambda: None, lambda: None)

  assert resultado is None
  assert any('Torre Arcana' in m for m in mensagens)


def test_entrar_torre_arcana_liberada_retorna_sinal():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.torre_arcana_liberada = True

  resultado = jogo._entrar_torre_arcana_callback(
      personagem, lambda *_a, **_k: None, lambda: None, lambda: None)

  assert resultado == 'torre_arcana'


def test_entrar_abismo_submerso_bloqueado_sem_liberar():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  mensagens = []

  resultado = jogo._entrar_abismo_submerso_callback(
      personagem, mensagens.append, lambda: None, lambda: None)

  assert resultado is None
  assert any('Abismo Submerso' in m for m in mensagens)


def test_entrar_abismo_submerso_liberado_retorna_sinal():
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.abismo_submerso_liberado = True

  resultado = jogo._entrar_abismo_submerso_callback(
      personagem, lambda *_a, **_k: None, lambda: None, lambda: None)

  assert resultado == 'abismo_submerso'


def test_torre_arcana_e_abismo_submerso_nao_aparecem_mais_na_vila_de_habusken():
  """As duas dungeons se mudaram pro mapa de Vethgard — não fazia sentido
  narrativo elas continuarem só no menu de Habusken."""
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.torre_arcana_liberada = True
  personagem.abismo_submerso_liberado = True

  opcoes, _secoes = jogo._opcoes_e_secoes_vila(personagem)

  assert 'Torre Arcana' not in opcoes
  assert 'Abismo Submerso' not in opcoes


def test_tela_vethgard_entra_na_torre_arcana_e_libera_abismo_submerso(monkeypatch):
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.torre_arcana_liberada = True

  respostas_mapa = iter(['torre_arcana', None])
  monkeypatch.setattr(jogo.mundo, 'explorar_mapa', lambda *_a, **_k: next(respostas_mapa))

  def _fake_tela_dungeon(p, _dungeon_id, _slots):
    p.chefes_derrotados.append('O Arquiteto')

  monkeypatch.setattr(jogo, '_tela_dungeon', _fake_tela_dungeon)
  monkeypatch.setattr(jogo, '_talvez_autosalvar', lambda *_a, **_k: None)

  jogo._tela_vethgard(personagem, slots=[None, None, None])

  assert personagem.abismo_submerso_liberado is True


def test_tela_vethgard_derrotar_kraken_libera_cratera_e_mostra_epilogo_uma_vez(monkeypatch):
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.abismo_submerso_liberado = True

  respostas_mapa = iter(['abismo_submerso', None])
  monkeypatch.setattr(jogo.mundo, 'explorar_mapa', lambda *_a, **_k: next(respostas_mapa))

  def _fake_tela_dungeon(p, _dungeon_id, _slots):
    p.chefes_derrotados.append('Kraken Ancestral')

  monkeypatch.setattr(jogo, '_tela_dungeon', _fake_tela_dungeon)
  monkeypatch.setattr(jogo, '_talvez_autosalvar', lambda *_a, **_k: None)
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  mensagens = []
  monkeypatch.setattr('builtins.print', lambda *args, **_k: mensagens.append(' '.join(str(a) for a in args)))

  jogo._tela_vethgard(personagem, slots=[None, None, None])

  assert personagem.cratera_vhalos_liberado is True
  assert personagem.abismo_epilogo_mostrado is True
  assert any('Abismo Submerso' in m or 'águas' in m.lower() for m in mensagens)


def test_eventos_do_mundo_aberto_referenciam_npcs_e_sidequests_validos(monkeypatch):
  """Regressão contra erro de digitação: cada NPC/sidequest usado nos mapas
  do mundo aberto só quebraria em tempo real, ao pisar naquela célula, sem
  esse teste — aqui é pego na hora. `menu_padrao` é mockado porque os
  eventos de NPC com sidequest usam o menu de setas de verdade por padrão
  (travaria esperando teclado); `mostrar_falas` é mockado porque senão anima
  o diálogo palavra por palavra de verdade (real, mas deixaria o teste lento
  sem trazer nenhuma cobertura a mais)."""
  from rpg.dados.npcs import NPCS
  from rpg.dados.sidequests import SIDEQUESTS

  monkeypatch.setattr('rpg.sistemas.mundo.menu_padrao', lambda *_a, **_k: None)
  monkeypatch.setattr('rpg.sistemas.mundo.mostrar_falas', lambda *_a, **_k: None)
  # os eventos de "prédio" de Vethgard (loja/curandeira/mestre) abrem telas de
  # verdade, que por padrão usam menu/input reais — mockadas aqui também.
  monkeypatch.setattr(jogo.loja, 'loja_acessorios_vethgard', lambda *_a, **_k: None)
  monkeypatch.setattr(jogo.cidade, 'tela_curandeira', lambda *_a, **_k: None)
  monkeypatch.setattr(jogo.cidade, 'tela_mestre_vethgard', lambda *_a, **_k: None)
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  for eventos in (jogo._eventos_ilyrath(), jogo._eventos_vethgard()):
    for caractere, callback in eventos.items():
      # cada callback tem que ser chamável sem estourar exceção, com um
      # personagem "zerado" e todas as dependências injetadas mockadas.
      callback(personagem, lambda *_a, **_k: None, lambda: None, lambda: None)

  # nomes usados nas fábricas de evento precisam bater com os catálogos —
  # checagem direta, sem depender de nenhuma exceção ter estourado acima.
  for chave_npc in ('arquivista_sorel', 'orfao_mikel', 'guarda_vethgard', 'velho_caminhante',
                     'capita_wren', 'estudioso_aldric'):
    assert chave_npc in NPCS
  for sidequest_id in ('cristal_para_sorel', 'lenco_da_familia', 'ecos_da_cantiga',
                        'ameaca_gelada', 'eco_do_abismo'):
    assert sidequest_id in SIDEQUESTS


def test_navegacao_real_da_entrada_ate_o_primeiro_bau_de_ilyrath():
  """Regressão de mapa: um obstáculo mal posicionado no caminho entre a
  entrada e um ponto de interesse deixaria aquele ponto inalcançável sem
  nenhum teste unitário pegar isso (eles chamam os callbacks direto, sem
  navegar de verdade). Aqui anda-se pelo mapa real de verdade."""
  from rpg.dados.mapas_mundo import MAPA_ILYRATH
  from rpg.sistemas import mundo as sistema_mundo

  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  chamadas = []
  eventos = {'1': lambda *_a: chamadas.append('bau') or None}
  # entrada em (9, 1), baú '1' em (4, 12) — sobe 5, depois vai à direita 11.
  fila = ['cima'] * 5 + ['direita'] * 11

  sistema_mundo.explorar_mapa(
      personagem, MAPA_ILYRATH, eventos, 'teste',
      escrever=lambda *_a, **_k: None,
      leitor_tecla=lambda: (fila.pop(0) if fila else 'esc'),
      limpar=lambda: None, aguardar=lambda: None)

  assert chamadas == ['bau']


def test_mapas_do_mundo_aberto_tem_todos_os_caracteres_de_evento_cobertos():
  """Todo caractere não-terreno (`.`, '#', 'E', 'F') que aparece no mapa
  precisa ter um evento registrado — senão o jogador pisa nele e nada
  acontece (ou pior, ele fica preso se o caractere não for andável)."""
  from rpg.dados.mapas_mundo import MAPA_ILYRATH, MAPA_VETHGARD

  caracteres_ilyrath = {c for linha in MAPA_ILYRATH for c in linha} - {'.', '#', 'E', 'F'}
  assert caracteres_ilyrath == set(jogo._eventos_ilyrath())

  caracteres_vethgard = {c for linha in MAPA_VETHGARD for c in linha} - {'.', '#', 'E', 'F'}
  assert caracteres_vethgard == set(jogo._eventos_vethgard())


def test_derrotar_vashtar_mostra_epilogo_uma_unica_vez(monkeypatch):
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.cratera_vhalos_liberado = True

  # Simula: o jogador viaja para a Cratera, a "dungeon" (mockada) resulta na
  # derrota de Vashtar, e depois o jogador aperta Esc pra sair do mapa do mundo.
  respostas_mapa = iter(['cratera', None])
  monkeypatch.setattr(jogo.mundo, 'explorar_mapa', lambda *_a, **_k: next(respostas_mapa))

  def _fake_tela_dungeon(p, _dungeon_id, _slots):
    p.chefes_derrotados.append('Vashtar, o Rei Cinza')

  monkeypatch.setattr(jogo, '_tela_dungeon', _fake_tela_dungeon)
  monkeypatch.setattr(jogo, 'limpar_tela', lambda: None)
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  mensagens = []
  monkeypatch.setattr('builtins.print', lambda *args, **_k: mensagens.append(' '.join(str(a) for a in args)))

  jogo._tela_mapa_mundo(personagem, slots=[None, None, None])

  assert personagem.historia_concluida is True
  assert any('Vashtar' in m for m in mensagens)


def test_vila_nao_tem_mais_guia_elemental_como_opcao_propria():
  """O Guia Elemental virou um tópico dentro do Tutorial — não deveria mais
  aparecer solto na vila."""
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  opcoes, _secoes = jogo._opcoes_e_secoes_vila(personagem)
  assert 'Guia Elemental' not in opcoes


def test_todas_as_opcoes_da_vila_sao_reconhecidas_por_executar_acao(monkeypatch):
  """Regressão: uma opção presente na lista da vila mas sem `elif`
  correspondente em `_executar_acao_vila` simplesmente não faria nada ao
  ser escolhida."""
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  personagem.torre_arcana_liberada = True
  personagem.abismo_submerso_liberado = True
  personagem.nivel = 999  # garante a opção "Especialização" também

  chamadas = []
  for chave in ('_tela_loja', '_tela_dungeon', '_tela_mapa_mundo'):
    monkeypatch.setattr(jogo, chave, lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_mestre_habusken', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_personagem', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_casa', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_desbloquear_habilidades', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_status', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_inventario', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_tutorial', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_guilda', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_curandeira', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_bau', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_crafting', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_ferreiro', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_especializacao', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_estatisticas', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_mapa_progresso', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.cidade, 'tela_diario_conquistas', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo, 'salvar_slots', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr(jogo.mundo, 'mostrar_falas', lambda *_a, **_k: chamadas.append(1))
  monkeypatch.setattr('builtins.input', lambda *_a, **_k: '')
  monkeypatch.setattr('builtins.print', lambda *_a, **_k: None)

  opcoes, _secoes = jogo._opcoes_e_secoes_vila(personagem)
  acoes_testaveis = [a for a in opcoes if a != 'Salvar e Sair']

  for acao in acoes_testaveis:
    antes = len(chamadas)
    jogo._executar_acao_vila(acao, personagem, slots=[None, None, None])
    assert len(chamadas) == antes + 1, f'"{acao}" não disparou nenhuma tela'


def test_vila_lembra_a_ultima_opcao_selecionada(monkeypatch):
  """Pedido do usuário: voltar pro menu da vila depois de sair de uma tela
  deve manter aquele item já selecionado, em vez de resetar pro topo."""
  personagem = Personagem(nome='teste', classe='Cavaleiro', raca='Humano')
  indices_iniciais_vistos = []
  respostas = iter([3, 3])  # escolhe índice 3 de novo na 2ª volta ao menu

  def _fake_menu(_titulo, _opcoes, *, indice_inicial=0, com_voltar=True, secoes=None):
    indices_iniciais_vistos.append(indice_inicial)
    return next(respostas)

  class _Para(Exception):
    pass

  chamadas = []

  def _fake_executar(acao, _p, _slots):
    chamadas.append(acao)
    if len(chamadas) == 2:
      raise _Para()

  monkeypatch.setattr(jogo, 'menu_padrao', _fake_menu)
  monkeypatch.setattr(jogo, '_executar_acao_vila', _fake_executar)
  monkeypatch.setattr(jogo, '_talvez_autosalvar', lambda *_a, **_k: None)

  with pytest.raises(_Para):
    jogo._tela_vila(personagem, [None, None, None])

  # 1ª volta ao menu abre em 0 (padrão); a 2ª já abre no índice 3 escolhido
  # na volta anterior, em vez de resetar pro topo.
  assert indices_iniciais_vistos == [0, 3]
