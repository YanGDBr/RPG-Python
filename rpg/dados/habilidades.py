"""As 6 habilidades de cada classe: 3 iniciais + 3 desbloqueáveis com nível e moedas."""

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
  'Bola de Gelo': Habilidade(
      nome='Bola de Gelo', mana=35, dano_base=60, tipo='ataque', elemento='Gelo',
      efeito='Fraqueza', turnos_efeito=2, cooldown_max=2, nivel_minimo=10, preco=250,
      descricao='Arremessa uma bola de gelo que enfraquece o poder do inimigo.'),
  'Fogo do Dragão Elemental': Habilidade(
      nome='Fogo do Dragão Elemental', mana=100, dano_base=150, tipo='ataque', elemento='Fogo',
      efeito='Queimadura', turnos_efeito=2, cooldown_max=3, nivel_minimo=15, preco=500,
      descricao='Usa o poder do fogo do Dragão Elemental contra o inimigo.'),
  'Meteoro Arcano': Habilidade(
      nome='Meteoro Arcano', mana=140, dano_base=220, tipo='ataque', elemento='Fogo',
      bonus_critico=15, cooldown_max=4, nivel_minimo=25, preco=900,
      descricao='Invoca um meteoro flamejante direto do céu.'),

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
  'Golpe Atordoante': Habilidade(
      nome='Golpe Atordoante', mana=30, dano_base=50, tipo='ataque',
      efeito='Paralisia', turnos_efeito=1, cooldown_max=2, nivel_minimo=10, preco=250,
      descricao='Um golpe pesado que atordoa o inimigo.'),
  'Espada de Aura': Habilidade(
      nome='Espada de Aura', mana=80, dano_base=180, tipo='ataque', cooldown_max=3,
      nivel_minimo=15, preco=500,
      descricao='Investe a espada com Aura, uma variante mais poderosa da mana.'),
  'Fúria do Guerreiro': Habilidade(
      nome='Fúria do Guerreiro', mana=120, dano_base=230, tipo='ataque',
      bonus_critico=20, cooldown_max=4, nivel_minimo=25, preco=900,
      descricao='Um golpe desesperado com toda a fúria acumulada em batalha.'),

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
  'Flecha Perfurante': Habilidade(
      nome='Flecha Perfurante', mana=40, dano_base=90, tipo='ataque', cooldown_max=2,
      nivel_minimo=10, preco=250,
      descricao='Uma flecha reforçada que perfura qualquer armadura.'),
  'Flecha de Ponta Cristalizada Venenosa': Habilidade(
      nome='Flecha de Ponta Cristalizada Venenosa', mana=100, dano_base=150, tipo='ataque',
      efeito='Veneno', turnos_efeito=3, cooldown_max=3, nivel_minimo=15, preco=500,
      descricao='Uma flecha com ponta de cristal envenenada.'),
  'Chuva Mortal': Habilidade(
      nome='Chuva Mortal', mana=150, dano_base=30, tipo='ataque_multiplo',
      acertos_min=6, acertos_max=10, bonus_critico=15, cooldown_max=4,
      nivel_minimo=25, preco=900,
      descricao='Uma saraivada mortal de flechas cobre todo o campo de batalha.'),
}


HABILIDADES_INICIAIS = {
  'Mago': ['Missil Mágico', 'Chamas', 'Raio'],
  'Cavaleiro': ['Investida', 'Corte Fatal', 'Espada Mágica'],
  'Arqueiro': ['Flecha Rápida', 'Flecha Tripla', 'Chuva de Flechas'],
}

HABILIDADES_DESBLOQUEAVEIS = {
  'Mago': ['Bola de Gelo', 'Fogo do Dragão Elemental', 'Meteoro Arcano'],
  'Cavaleiro': ['Golpe Atordoante', 'Espada de Aura', 'Fúria do Guerreiro'],
  'Arqueiro': ['Flecha Perfurante', 'Flecha de Ponta Cristalizada Venenosa', 'Chuva Mortal'],
}
