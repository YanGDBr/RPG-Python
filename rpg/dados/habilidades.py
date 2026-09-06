"""Habilidades de cada classe: 3 iniciais (grátis) + uma árvore de
desbloqueáveis que vai do nível 3 até o pós-Rei Cinza (50+), pensada pra
sempre ter algo novo pra comprar cedo — não só lá na frente."""

from ..modelos.habilidade import Habilidade

HABILIDADES = {
  # ---------------------------------------------------------------- Mago
  'Missil Mágico': Habilidade(
      nome='Missil Mágico', mana=15, dano_base=15, tipo='ataque',
      descricao='Conjura uma bola de mana e joga no oponente a uma velocidade gigantesca.'),
  'Chamas': Habilidade(
      nome='Chamas', mana=25, dano_base=30, tipo='ataque', elemento='Fogo',
      efeito='Queimadura', turnos_efeito=3, cooldown_max=2,
      descricao='Conjura chamas e atira em direção ao alvo.'),
  'Raio': Habilidade(
      nome='Raio', mana=50, dano_base=80, tipo='ataque', elemento='Eletrico',
      efeito='Paralisia', turnos_efeito=1, cooldown_max=3,
      descricao='Convoca um raio dos céus para cair em cima do inimigo.'),
  'Lança de Gelo': Habilidade(
      nome='Lança de Gelo', mana=22, dano_base=35, tipo='ataque', elemento='Gelo',
      cooldown_max=1, nivel_minimo=3, preco=80,
      descricao='Uma lança de gelo afiada, rápida de conjurar.'),
  'Corrente Sombria': Habilidade(
      nome='Corrente Sombria', mana=28, dano_base=45, tipo='ataque', elemento='Sombrio',
      efeito='Fraqueza', turnos_efeito=2, cooldown_max=2, nivel_minimo=5, preco=120,
      descricao='Correntes de energia sombria que enfraquecem o inimigo.'),
  'Maré Arcana': Habilidade(
      nome='Maré Arcana', mana=32, dano_base=55, tipo='ataque', elemento='Agua',
      cooldown_max=2, nivel_minimo=7, preco=160,
      descricao='Uma onda de energia arcana em forma de água. Completa a roda elemental do Mago.'),
  'Bola de Gelo': Habilidade(
      nome='Bola de Gelo', mana=35, dano_base=60, tipo='ataque', elemento='Gelo',
      efeito='Fraqueza', turnos_efeito=2, cooldown_max=2, nivel_minimo=10, preco=250,
      descricao='Arremessa uma bola de gelo que enfraquece o poder do inimigo.'),
  'Explosão Congelante': Habilidade(
      nome='Explosão Congelante', mana=65, dano_base=100, tipo='ataque', elemento='Gelo',
      efeito='Vulnerabilidade', turnos_efeito=2, cooldown_max=3, nivel_minimo=12, preco=320,
      canalizavel=True,
      descricao='Uma explosão de gelo que deixa o inimigo mais vulnerável — pode ser canalizada.'),
  'Fogo do Dragão Elemental': Habilidade(
      nome='Fogo do Dragão Elemental', mana=100, dano_base=150, tipo='ataque', elemento='Fogo',
      efeito='Queimadura', turnos_efeito=2, cooldown_max=3, nivel_minimo=15, preco=500,
      descricao='Usa o poder do fogo do Dragão Elemental contra o inimigo.'),
  'Tempestade Sombria': Habilidade(
      nome='Tempestade Sombria', mana=110, dano_base=90, tipo='ataque_area', elemento='Sombrio',
      cooldown_max=3, nivel_minimo=18, preco=650,
      descricao='Uma tempestade de energia sombria que atinge todos os inimigos.'),
  'Maremoto': Habilidade(
      nome='Maremoto', mana=130, dano_base=200, tipo='ataque', elemento='Agua',
      efeito='Paralisia', turnos_efeito=1, cooldown_max=3, nivel_minimo=20, preco=750,
      descricao='Convoca um maremoto arcano que paralisa o inimigo.'),
  'Meteoro Arcano': Habilidade(
      nome='Meteoro Arcano', mana=140, dano_base=220, tipo='ataque', elemento='Fogo',
      bonus_critico=15, cooldown_max=4, nivel_minimo=25, preco=900,
      descricao='Invoca um meteoro flamejante direto do céu.'),
  'Convergência Elemental': Habilidade(
      nome='Convergência Elemental', mana=160, dano_base=250, tipo='ataque', elemento='Fisico',
      ignora_resistencia=True, bonus_critico=10, cooldown_max=4, nivel_minimo=35, preco=1400,
      descricao='Converge todos os elementos num só golpe que ignora qualquer resistência.'),
  'Fúria dos Quatro Elementos': Habilidade(
      nome='Fúria dos Quatro Elementos', mana=200, dano_base=150, tipo='ataque_area',
      elemento='Fisico', ignora_resistencia=True, cooldown_max=4, nivel_minimo=40, preco=1800,
      descricao='Desencadeia os quatro elementos de uma vez sobre todos os inimigos.'),
  'Olho da Tormenta': Habilidade(
      nome='Olho da Tormenta', mana=220, dano_base=270, tipo='ataque', elemento='Eletrico',
      efeito='Paralisia', turnos_efeito=2, cooldown_max=4, nivel_minimo=45, preco=2200,
      canalizavel=True,
      descricao='O centro de uma tempestade arcana — pode ser canalizada pra um golpe devastador.'),
  'Fogo Cinzento': Habilidade(
      nome='Fogo Cinzento', mana=170, dano_base=280, tipo='ataque', elemento='Fogo',
      efeito='Queimadura', turnos_efeito=3, cooldown_max=4, nivel_minimo=50, preco=2500,
      descricao='As chamas que consumiram o Rei Cinza, agora nas suas mãos.'),

  # ----------------------------------------------------------- Cavaleiro
  'Investida': Habilidade(
      nome='Investida', mana=15, dano_base=15, tipo='ataque',
      descricao='Faz uma rápida investida no oponente e o ataca.'),
  'Corte Fatal': Habilidade(
      nome='Corte Fatal', mana=20, dano_base=25, tipo='ataque',
      efeito='Sangramento', turnos_efeito=3, cooldown_max=2,
      descricao='Um corte profundo nas costas do oponente.'),
  'Espada Mágica': Habilidade(
      nome='Espada Mágica', mana=45, dano_base=100, tipo='ataque', cooldown_max=2,
      descricao='Um golpe com a espada investida de mana.'),
  'Golpe Duplo': Habilidade(
      nome='Golpe Duplo', mana=22, dano_base=20, tipo='ataque_multiplo',
      acertos_min=1, acertos_max=2, cooldown_max=1, nivel_minimo=3, preco=80,
      descricao='Dois golpes rápidos e certeiros.'),
  'Grito de Guerra': Habilidade(
      nome='Grito de Guerra', mana=0, custo_furia=20, dano_base=40, tipo='ataque',
      cooldown_max=1, nivel_minimo=5, preco=120,
      descricao='Um grito que assusta o inimigo e abre espaço pro golpe — seu primeiro gasto de Fúria.'),
  'Corte Giratório': Habilidade(
      nome='Corte Giratório', mana=45, dano_base=40, tipo='ataque_area', cooldown_max=2,
      nivel_minimo=7, preco=160,
      descricao='Um golpe giratório que acerta todos os inimigos ao redor.'),
  'Golpe Atordoante': Habilidade(
      nome='Golpe Atordoante', mana=30, dano_base=50, tipo='ataque',
      efeito='Paralisia', turnos_efeito=1, cooldown_max=2, nivel_minimo=10, preco=250,
      descricao='Um golpe pesado que atordoa o inimigo.'),
  'Golpe Sísmico': Habilidade(
      nome='Golpe Sísmico', mana=70, dano_base=110, tipo='ataque',
      efeito='Vulnerabilidade', turnos_efeito=2, cooldown_max=3, nivel_minimo=12, preco=320,
      canalizavel=True,
      descricao='Um golpe que racha o chão e deixa o inimigo exposto — pode ser canalizado.'),
  'Espada de Aura': Habilidade(
      nome='Espada de Aura', mana=80, dano_base=180, tipo='ataque', cooldown_max=3,
      nivel_minimo=15, preco=500,
      descricao='Investe a espada com Aura, uma variante mais poderosa da mana.'),
  'Investida Brutal': Habilidade(
      nome='Investida Brutal', mana=0, custo_furia=45, dano_base=190, tipo='ataque',
      cooldown_max=2, nivel_minimo=18, preco=650,
      descricao='Uma investida com toda a força bruta acumulada.'),
  'Lâmina Sangrenta': Habilidade(
      nome='Lâmina Sangrenta', mana=100, dano_base=195, tipo='ataque',
      efeito='Sangramento', turnos_efeito=3, cooldown_max=3, nivel_minimo=20, preco=750,
      descricao='Uma lâmina que abre um corte fundo e sangrento.'),
  'Fúria do Guerreiro': Habilidade(
      nome='Fúria do Guerreiro', mana=120, dano_base=230, tipo='ataque',
      bonus_critico=20, cooldown_max=4, nivel_minimo=25, preco=900,
      descricao='Um golpe desesperado com toda a fúria acumulada em batalha.'),
  'Corte do Destino': Habilidade(
      nome='Corte do Destino', mana=150, dano_base=250, tipo='ataque',
      bonus_critico=15, cooldown_max=4, nivel_minimo=35, preco=1400,
      descricao='Um corte que parece guiado pelo próprio destino.'),
  'Fúria Desmedida': Habilidade(
      nome='Fúria Desmedida', mana=0, custo_furia=70, dano_base=130, tipo='ataque_area',
      cooldown_max=3, nivel_minimo=40, preco=1800,
      descricao='Descarrega toda a fúria acumulada contra todos ao redor.'),
  'Julgamento de Aço': Habilidade(
      nome='Julgamento de Aço', mana=210, dano_base=270, tipo='ataque',
      ignora_resistencia=True, cooldown_max=4, nivel_minimo=45, preco=2200,
      canalizavel=True,
      descricao='Um golpe final que nenhuma resistência detém — pode ser canalizado.'),
  'Lâmina do Rei Caído': Habilidade(
      nome='Lâmina do Rei Caído', mana=140, dano_base=300, tipo='ataque', elemento='Fisico',
      bonus_critico=20, cooldown_max=4, nivel_minimo=50, preco=2500,
      descricao='Um golpe forjado no mesmo desespero que corrompeu um rei inteiro.'),

  # ------------------------------------------------------------- Arqueiro
  'Flecha Rápida': Habilidade(
      nome='Flecha Rápida', mana=20, dano_base=20, tipo='ataque',
      descricao='Atira uma flecha rápida que crava no peito do inimigo.'),
  'Flecha Tripla': Habilidade(
      nome='Flecha Tripla', mana=30, dano_base=20, tipo='ataque_multiplo',
      acertos_min=1, acertos_max=3, cooldown_max=2,
      descricao='Atira três flechas de uma vez no inimigo.'),
  'Chuva de Flechas': Habilidade(
      nome='Chuva de Flechas', mana=55, dano_base=20, tipo='ataque_multiplo',
      acertos_min=5, acertos_max=8, cooldown_max=3,
      descricao='Atira flechas em cima do oponente criando uma chuva de flechas.'),
  'Flecha Dupla': Habilidade(
      nome='Flecha Dupla', mana=22, dano_base=20, tipo='ataque_multiplo',
      acertos_min=1, acertos_max=2, cooldown_max=1, nivel_minimo=3, preco=80,
      descricao='Duas flechas rápidas, uma logo depois da outra.'),
  'Marcar Alvo': Habilidade(
      nome='Marcar Alvo', mana=25, dano_base=20, tipo='ataque',
      efeito='Marcado', turnos_efeito=3, cooldown_max=2, nivel_minimo=5, preco=120,
      descricao='Marca o inimigo — qualquer ataque nele causa mais dano enquanto durar a marca.'),
  'Rajada de Flechas': Habilidade(
      nome='Rajada de Flechas', mana=45, dano_base=35, tipo='ataque_area', cooldown_max=2,
      nivel_minimo=7, preco=160,
      descricao='Uma rajada que cobre uma área inteira de flechas.'),
  'Flecha Perfurante': Habilidade(
      nome='Flecha Perfurante', mana=40, dano_base=90, tipo='ataque', cooldown_max=2,
      nivel_minimo=10, preco=250,
      descricao='Uma flecha reforçada que perfura qualquer armadura.'),
  'Tiro Carregado': Habilidade(
      nome='Tiro Carregado', mana=0, custo_foco=30, dano_base=110, tipo='ataque',
      cooldown_max=2, nivel_minimo=12, preco=320,
      descricao='Um tiro carregado com todo o Foco acumulado — seu primeiro gasto de Foco.'),
  'Flecha de Ponta Cristalizada Venenosa': Habilidade(
      nome='Flecha de Ponta Cristalizada Venenosa', mana=100, dano_base=150, tipo='ataque',
      efeito='Veneno', turnos_efeito=3, cooldown_max=3, nivel_minimo=15, preco=500,
      descricao='Uma flecha com ponta de cristal envenenada.'),
  'Flecha Perfurante Aprimorada': Habilidade(
      nome='Flecha Perfurante Aprimorada', mana=90, dano_base=190, tipo='ataque',
      ignora_resistencia=True, cooldown_max=3, nivel_minimo=18, preco=650,
      descricao='Uma versão aprimorada da flecha perfurante, ainda mais afiada.'),
  'Chuva Perfurante': Habilidade(
      nome='Chuva Perfurante', mana=140, dano_base=70, tipo='ataque_area', cooldown_max=3,
      nivel_minimo=20, preco=750,
      descricao='Uma chuva de flechas perfurantes sobre todos os inimigos.'),
  'Chuva Mortal': Habilidade(
      nome='Chuva Mortal', mana=150, dano_base=30, tipo='ataque_multiplo',
      acertos_min=6, acertos_max=10, bonus_critico=15, cooldown_max=4,
      nivel_minimo=25, preco=900,
      descricao='Uma saraivada mortal de flechas cobre todo o campo de batalha.'),
  'Tiro do Caçador': Habilidade(
      nome='Tiro do Caçador', mana=0, custo_foco=55, dano_base=250, tipo='ataque',
      sempre_critico=True, cooldown_max=3, nivel_minimo=35, preco=1400,
      descricao='Um tiro certeiro de caçador — sempre crítico.'),
  'Saraivada Final': Habilidade(
      nome='Saraivada Final', mana=180, dano_base=30, tipo='ataque_multiplo',
      acertos_min=8, acertos_max=12, cooldown_max=4, nivel_minimo=40, preco=1800,
      descricao='A maior saraivada de flechas que um Arqueiro pode disparar.'),
  'Flecha Perfeita': Habilidade(
      nome='Flecha Perfeita', mana=0, custo_foco=70, dano_base=270, tipo='ataque',
      sempre_critico=True, cooldown_max=4, nivel_minimo=45, preco=2200,
      canalizavel=True,
      descricao='A flecha perfeita — sempre crítica, e pode ser canalizada pra um dano ainda maior.'),
  'Flecha do Juízo': Habilidade(
      nome='Flecha do Juízo', mana=150, dano_base=260, tipo='ataque', elemento='Fisico',
      ignora_resistencia=True, cooldown_max=4, nivel_minimo=50, preco=2500,
      descricao='Perfura qualquer resistência — nem coroas cinzentas a detêm.'),

  # ------------------------------------------- Especializações (nível 30+)
  # Concedidas automaticamente ao escolher a especialização — não precisam
  # ser compradas/desbloqueadas como as outras.
  'Explosão Solar': Habilidade(
      nome='Explosão Solar', mana=130, dano_base=200, tipo='ataque', elemento='Fogo',
      efeito='Queimadura', turnos_efeito=3, cooldown_max=4,
      descricao='Uma explosão solar avassaladora, marca do Piromante.'),
  'Fúria Glacial': Habilidade(
      nome='Fúria Glacial', mana=110, dano_base=170, tipo='ataque', elemento='Gelo',
      efeito='Vulnerabilidade', turnos_efeito=3, cooldown_max=3,
      descricao='Uma nevasca que fere e deixa o inimigo mais vulnerável, marca do Criomante.'),
  'Julgamento': Habilidade(
      nome='Julgamento', mana=100, dano_base=140, tipo='ataque', elemento='Fisico',
      cura_percentual_usuario=15, efeito_no_usuario='Regeneração', turnos_efeito_no_usuario=3,
      cooldown_max=3, descricao='Um golpe sagrado que fere o inimigo e cura o Paladino.'),
  'Fúria Sanguinária': Habilidade(
      nome='Fúria Sanguinária', mana=0, custo_furia=100, dano_base=260, tipo='ataque',
      elemento='Fisico', cooldown_max=2,
      descricao='Um golpe desesperado alimentado por toda a fúria acumulada em batalha.'),
  'Tiro Certeiro': Habilidade(
      nome='Tiro Certeiro', mana=60, dano_base=110, tipo='ataque', elemento='Fisico',
      sempre_critico=True, cooldown_max=2,
      descricao='Uma flecha certeira que sempre acerta em cheio, marca do Batedor.'),
  'Tiro Perfurante': Habilidade(
      nome='Tiro Perfurante', mana=90, dano_base=160, tipo='ataque', elemento='Fisico',
      ignora_resistencia=True, cooldown_max=3,
      descricao='Uma flecha que ignora qualquer resistência do inimigo.'),
}


HABILIDADES_INICIAIS = {
  'Mago': ['Missil Mágico', 'Chamas', 'Raio'],
  'Cavaleiro': ['Investida', 'Corte Fatal', 'Espada Mágica'],
  'Arqueiro': ['Flecha Rápida', 'Flecha Tripla', 'Chuva de Flechas'],
}

HABILIDADES_DESBLOQUEAVEIS = {
  'Mago': ['Lança de Gelo', 'Corrente Sombria', 'Maré Arcana', 'Bola de Gelo',
           'Explosão Congelante', 'Fogo do Dragão Elemental', 'Tempestade Sombria', 'Maremoto',
           'Meteoro Arcano', 'Convergência Elemental', 'Fúria dos Quatro Elementos',
           'Olho da Tormenta', 'Fogo Cinzento'],
  'Cavaleiro': ['Golpe Duplo', 'Grito de Guerra', 'Corte Giratório', 'Golpe Atordoante',
                'Golpe Sísmico', 'Espada de Aura', 'Investida Brutal', 'Lâmina Sangrenta',
                'Fúria do Guerreiro', 'Corte do Destino', 'Fúria Desmedida', 'Julgamento de Aço',
                'Lâmina do Rei Caído'],
  'Arqueiro': ['Flecha Dupla', 'Marcar Alvo', 'Rajada de Flechas', 'Flecha Perfurante',
               'Tiro Carregado', 'Flecha de Ponta Cristalizada Venenosa',
               'Flecha Perfurante Aprimorada', 'Chuva Perfurante', 'Chuva Mortal',
               'Tiro do Caçador', 'Saraivada Final', 'Flecha Perfeita', 'Flecha do Juízo'],
}
