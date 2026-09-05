"""Todos os monstros do jogo, organizados por dungeon e andar."""

from ..modelos.monstro import MonstroBase

MONSTROS = {
  # =====================================================  Habusken — Andar 1
  'Slime': MonstroBase(
      nome='Slime', vida_maxima=50, ataque_min=5, ataque_max=8, nivel=1,
      elemento='Fisico', fraquezas=('Fogo',), resistencias=('Fisico',),
      exp_min=10, exp_max=15, moedas_min=5, moedas_max=15,
      drops_item=(('Gosma de Slime', 0.5),),
      descricoes_ataque=('O Slime dá uma cabeçada em você', 'O Slime ataca sua perna e te derruba')),
  'Kobold': MonstroBase(
      nome='Kobold', vida_maxima=60, ataque_min=8, ataque_max=10, nivel=3,
      exp_min=16, exp_max=25, moedas_min=10, moedas_max=20,
      drops_item=(('Presa de Lobo', 0.2),),
      descricoes_ataque=('O Kobold te corta com uma adaga', 'O Kobold perfura sua costela')),
  'Lobo': MonstroBase(
      nome='Lobo', vida_maxima=65, ataque_min=10, ataque_max=13, nivel=4,
      fraquezas=('Fogo',),
      exp_min=18, exp_max=28, moedas_min=13, moedas_max=23,
      drops_item=(('Presa de Lobo', 0.5),),
      descricoes_ataque=('O Lobo dá uma investida e te morde ferozmente', 'O Lobo te ataca com suas garras')),
  'Slime Gigante': MonstroBase(
      nome='Slime Gigante', vida_maxima=150, ataque_min=20, ataque_max=25, nivel=10,
      fraquezas=('Fogo',), resistencias=('Fisico',), chefe=True,
      exp_min=30, exp_max=50, moedas_min=20, moedas_max=35,
      drops_item=(('Gosma de Slime', 1.0),),
      descricoes_ataque=('O Slime Gigante pula e te esmaga',
                          'O Slime Gigante dá uma rápida investida e te joga contra a parede')),

  # =====================================================  Habusken — Andar 2
  'Goblin': MonstroBase(
      nome='Goblin', vida_maxima=80, ataque_min=8, ataque_max=13, nivel=5,
      exp_min=20, exp_max=30, moedas_min=15, moedas_max=30,
      descricoes_ataque=('O Goblin desaparece na escuridão e golpeia você por trás',
                          'O Goblin tenta perfurar sua perna mas acerta só de raspão')),
  'Esqueleto': MonstroBase(
      nome='Esqueleto', vida_maxima=100, ataque_min=13, ataque_max=17, nivel=8,
      fraquezas=('Fogo',), resistencias=('Fisico',),
      exp_min=25, exp_max=35, moedas_min=20, moedas_max=35,
      drops_item=(('Ectoplasma', 0.15),),
      descricoes_ataque=('O Esqueleto atira uma flecha na sua perna', 'O Esqueleto atira uma flecha em seu braço')),
  'Kobold Mago': MonstroBase(
      nome='Kobold Mago', vida_maxima=110, ataque_min=17, ataque_max=20, nivel=10,
      elemento='Fogo', fraquezas=('Gelo',), resistencias=('Fogo',),
      exp_min=30, exp_max=40, moedas_min=25, moedas_max=50,
      efeito_aplicado='Queimadura', turnos_efeito_aplicado=2,
      descricoes_ataque=('O Kobold Mago conjura uma bola de fogo em você [Queimadura]',
                          'O Kobold Mago conjura um míssil mágico em sua direção')),
  'Goblin Xamã': MonstroBase(
      nome='Goblin Xamã', vida_maxima=170, ataque_min=30, ataque_max=40, nivel=15,
      elemento='Fogo', fraquezas=('Gelo',), resistencias=('Fogo',), chefe=True,
      exp_min=50, exp_max=80, moedas_min=40, moedas_max=80,
      drops_item=(('Cristal Arcano', 0.3),),
      efeito_aplicado='Queimadura', turnos_efeito_aplicado=2,
      descricoes_ataque=('O Goblin Xamã aumenta sua própria vida',
                          'O Goblin Xamã conjura espinhos flamejantes em sua direção [Queimadura]')),

  # =====================================================  Habusken — Andar 3
  'Golem de Pedra': MonstroBase(
      nome='Golem de Pedra', vida_maxima=220, ataque_min=35, ataque_max=45, nivel=16,
      resistencias=('Fisico',), fraquezas=('Eletrico',),
      exp_min=55, exp_max=75, moedas_min=45, moedas_max=70,
      descricoes_ataque=('O Golem de Pedra desfere um soco pesado', 'O Golem de Pedra pisa forte no chão')),
  'Aranha Gigante': MonstroBase(
      nome='Aranha Gigante', vida_maxima=200, ataque_min=38, ataque_max=48, nivel=18,
      fraquezas=('Fogo',), efeito_aplicado='Veneno', turnos_efeito_aplicado=3,
      exp_min=60, exp_max=80, moedas_min=45, moedas_max=75,
      drops_item=(('Presa de Lobo', 0.2),),
      descricoes_ataque=('A Aranha Gigante crava suas presas em você [Veneno]',
                          'A Aranha Gigante te enrola em teia')),
  'Orc Guerreiro': MonstroBase(
      nome='Orc Guerreiro', vida_maxima=250, ataque_min=40, ataque_max=50, nivel=20,
      exp_min=65, exp_max=90, moedas_min=50, moedas_max=80,
      descricoes_ataque=('O Orc Guerreiro dá um machadada', 'O Orc Guerreiro avança com o escudo')),
  'Orc Chefe': MonstroBase(
      nome='Orc Chefe', vida_maxima=400, ataque_min=55, ataque_max=70, nivel=22,
      fraquezas=('Eletrico',), resistencias=('Fisico',), chefe=True,
      exp_min=100, exp_max=150, moedas_min=90, moedas_max=140,
      drops_item=(('Presa de Lobo', 0.4),),
      descricoes_ataque=('O Orc Chefe dá um golpe devastador com seu machado gigante',
                          'O Orc Chefe berra e avança com fúria')),

  # =====================================================  Habusken — Andar 4
  'Zumbi': MonstroBase(
      nome='Zumbi', vida_maxima=280, ataque_min=45, ataque_max=55, nivel=21,
      elemento='Sombrio', fraquezas=('Fogo',), resistencias=('Sombrio',),
      efeito_aplicado='Veneno', turnos_efeito_aplicado=2,
      exp_min=70, exp_max=95, moedas_min=55, moedas_max=85,
      drops_item=(('Ectoplasma', 0.3),),
      descricoes_ataque=('O Zumbi te morde com sua boca podre [Veneno]', 'O Zumbi te agarra com as duas mãos')),
  'Fantasma': MonstroBase(
      nome='Fantasma', vida_maxima=260, ataque_min=50, ataque_max=60, nivel=23,
      elemento='Sombrio', fraquezas=('Eletrico',), resistencias=('Fisico',),
      exp_min=75, exp_max=100, moedas_min=60, moedas_max=90,
      drops_item=(('Ectoplasma', 0.5),),
      descricoes_ataque=('O Fantasma atravessa você causando um frio profundo',
                          'O Fantasma solta um grito apavorante')),
  'Cavaleiro Amaldiçoado': MonstroBase(
      nome='Cavaleiro Amaldiçoado', vida_maxima=320, ataque_min=55, ataque_max=65, nivel=25,
      elemento='Sombrio', fraquezas=('Fogo',), resistencias=('Sombrio',),
      exp_min=85, exp_max=115, moedas_min=70, moedas_max=100,
      descricoes_ataque=('O Cavaleiro Amaldiçoado desfere um golpe de espada amaldiçoada',
                          'O Cavaleiro Amaldiçoado avança montado em seu corcel espectral')),
  'Cavaleiro da Morte': MonstroBase(
      nome='Cavaleiro da Morte', vida_maxima=550, ataque_min=75, ataque_max=95, nivel=28,
      elemento='Sombrio', fraquezas=('Fogo',), resistencias=('Sombrio', 'Fisico'), chefe=True,
      exp_min=140, exp_max=190, moedas_min=120, moedas_max=180,
      drops_item=(('Ectoplasma', 0.6), ('Cristal Arcano', 0.25)),
      descricoes_ataque=('O Cavaleiro da Morte ergue sua espada e a crava no chão, abrindo fendas sombrias',
                          'O Cavaleiro da Morte avança com um golpe giratório')),

  # =====================================================  Habusken — Andar 5
  'Wyvern Jovem': MonstroBase(
      nome='Wyvern Jovem', vida_maxima=380, ataque_min=65, ataque_max=80, nivel=26,
      elemento='Fogo', fraquezas=('Gelo',), resistencias=('Fogo',),
      exp_min=100, exp_max=135, moedas_min=85, moedas_max=120,
      descricoes_ataque=('O Wyvern Jovem mergulha do ar e te ataca com as garras',
                          'O Wyvern Jovem cospe uma rajada de fogo [Queimadura]'),
      efeito_aplicado='Queimadura', turnos_efeito_aplicado=2),
  'Salamandra de Fogo': MonstroBase(
      nome='Salamandra de Fogo', vida_maxima=400, ataque_min=70, ataque_max=85, nivel=28,
      elemento='Fogo', fraquezas=('Gelo',), resistencias=('Fogo',),
      exp_min=105, exp_max=140, moedas_min=90, moedas_max=125,
      drops_item=(('Escama de Salamandra', 0.6),),
      descricoes_ataque=('A Salamandra de Fogo te envolve em chamas [Queimadura]',
                          'A Salamandra de Fogo chicoteia com a cauda flamejante'),
      efeito_aplicado='Queimadura', turnos_efeito_aplicado=2),
  'Golem de Obsidiana': MonstroBase(
      nome='Golem de Obsidiana', vida_maxima=450, ataque_min=75, ataque_max=90, nivel=30,
      elemento='Fogo', fraquezas=('Gelo',), resistencias=('Fisico', 'Fogo'),
      exp_min=115, exp_max=150, moedas_min=95, moedas_max=130,
      descricoes_ataque=('O Golem de Obsidiana desfere um golpe de lava incandescente',
                          'O Golem de Obsidiana esmaga o chão, espalhando cacos afiados')),
  'Dragão Ancião de Habusken': MonstroBase(
      nome='Dragão Ancião de Habusken', vida_maxima=800, ataque_min=100, ataque_max=130, nivel=35,
      elemento='Fogo', fraquezas=('Gelo',), resistencias=('Fogo', 'Fisico'), chefe=True,
      exp_min=250, exp_max=340, moedas_min=220, moedas_max=320,
      drops_item=(('Núcleo do Dragão Ancião', 1.0), ('Escama de Salamandra', 0.8)),
      efeito_aplicado='Queimadura', turnos_efeito_aplicado=3,
      descricoes_ataque=('O Dragão Ancião solta um rugido e cospe uma baforada de fogo ancestral [Queimadura]',
                          'O Dragão Ancião bate as asas e mergulha sobre você com toda sua força')),

  # =====================================================  Torre Arcana — Andar 1
  'Aprendiz Rebelde': MonstroBase(
      nome='Aprendiz Rebelde', vida_maxima=420, ataque_min=80, ataque_max=95, nivel=31,
      fraquezas=('Sombrio',),
      exp_min=120, exp_max=160, moedas_min=100, moedas_max=140,
      descricoes_ataque=('O Aprendiz Rebelde conjura uma explosão instável',
                          'O Aprendiz Rebelde ataca com um cajado improvisado')),
  'Constructo Arcano': MonstroBase(
      nome='Constructo Arcano', vida_maxima=460, ataque_min=85, ataque_max=100, nivel=33,
      elemento='Eletrico', fraquezas=('Gelo',), resistencias=('Eletrico',),
      exp_min=125, exp_max=165, moedas_min=105, moedas_max=145,
      drops_item=(('Cristal Arcano', 0.3),),
      descricoes_ataque=('O Constructo Arcano dispara um raio de energia',
                          'O Constructo Arcano avança com braços mecânicos')),
  'Grimório Vivo': MonstroBase(
      nome='Grimório Vivo', vida_maxima=440, ataque_min=90, ataque_max=105, nivel=35,
      elemento='Sombrio', fraquezas=('Fogo',), resistencias=('Sombrio',),
      exp_min=130, exp_max=170, moedas_min=110, moedas_max=150,
      descricoes_ataque=('O Grimório Vivo recita um feitiço amaldiçoado',
                          'O Grimório Vivo bate as páginas afiadas contra você')),
  'Arquimago Renegado': MonstroBase(
      nome='Arquimago Renegado', vida_maxima=700, ataque_min=110, ataque_max=140, nivel=38,
      elemento='Eletrico', fraquezas=('Fisico',), resistencias=('Eletrico', 'Sombrio'), chefe=True,
      exp_min=280, exp_max=360, moedas_min=230, moedas_max=330,
      drops_item=(('Cristal Arcano', 0.7),),
      descricoes_ataque=('O Arquimago Renegado conjura uma tempestade de raios',
                          'O Arquimago Renegado invoca lâminas arcanas flutuantes')),

  # =====================================================  Torre Arcana — Andar 2
  'Elemental de Gelo': MonstroBase(
      nome='Elemental de Gelo', vida_maxima=480, ataque_min=95, ataque_max=110, nivel=36,
      elemento='Gelo', fraquezas=('Fogo',), resistencias=('Gelo',),
      exp_min=135, exp_max=175, moedas_min=115, moedas_max=155,
      descricoes_ataque=('O Elemental de Gelo lança estilhaços congelantes',
                          'O Elemental de Gelo congela o chão ao seu redor')),
  'Elemental de Raio': MonstroBase(
      nome='Elemental de Raio', vida_maxima=500, ataque_min=100, ataque_max=115, nivel=38,
      elemento='Eletrico', fraquezas=('Fisico',), resistencias=('Eletrico',),
      exp_min=140, exp_max=180, moedas_min=120, moedas_max=160,
      descricoes_ataque=('O Elemental de Raio dispara uma descarga elétrica',
                          'O Elemental de Raio se teletransporta e ataca por trás')),
  'Guardião Espectral': MonstroBase(
      nome='Guardião Espectral', vida_maxima=520, ataque_min=105, ataque_max=120, nivel=40,
      elemento='Sombrio', fraquezas=('Fogo',), resistencias=('Fisico',),
      exp_min=145, exp_max=185, moedas_min=125, moedas_max=165,
      drops_item=(('Ectoplasma', 0.4),),
      descricoes_ataque=('O Guardião Espectral atravessa sua defesa',
                          'O Guardião Espectral solta um lamento gélido')),
  'Guardiã da Torre': MonstroBase(
      nome='Guardiã da Torre', vida_maxima=850, ataque_min=130, ataque_max=160, nivel=43,
      elemento='Gelo', fraquezas=('Fogo',), resistencias=('Gelo', 'Sombrio'), chefe=True,
      exp_min=320, exp_max=400, moedas_min=260, moedas_max=360,
      drops_item=(('Cristal Arcano', 0.7),),
      descricoes_ataque=('A Guardiã da Torre invoca lanças de gelo eterno',
                          'A Guardiã da Torre desce à sua frente como um espectro de gelo')),

  # =====================================================  Torre Arcana — Andar 3
  'Homúnculo': MonstroBase(
      nome='Homúnculo', vida_maxima=540, ataque_min=110, ataque_max=125, nivel=41,
      fraquezas=('Fogo',),
      exp_min=150, exp_max=195, moedas_min=130, moedas_max=170,
      descricoes_ataque=('O Homúnculo ataca com força bruta descontrolada',
                          'O Homúnculo cospe ácido corrosivo')),
  'Golem Arcano': MonstroBase(
      nome='Golem Arcano', vida_maxima=580, ataque_min=115, ataque_max=130, nivel=43,
      elemento='Eletrico', fraquezas=('Gelo',), resistencias=('Eletrico',),
      exp_min=155, exp_max=200, moedas_min=135, moedas_max=175,
      drops_item=(('Cristal Arcano', 0.4),),
      descricoes_ataque=('O Golem Arcano libera uma onda de choque mágica',
                          'O Golem Arcano avança com punhos flamejantes de runas')),
  'Espectro do Vazio': MonstroBase(
      nome='Espectro do Vazio', vida_maxima=600, ataque_min=120, ataque_max=135, nivel=45,
      elemento='Sombrio', fraquezas=('Fogo',), resistencias=('Sombrio', 'Fisico'),
      exp_min=160, exp_max=205, moedas_min=140, moedas_max=180,
      descricoes_ataque=('O Espectro do Vazio abre uma fenda de escuridão pura',
                          'O Espectro do Vazio sussurra e drena sua força vital')),
  'O Arquiteto': MonstroBase(
      nome='O Arquiteto', vida_maxima=1200, ataque_min=150, ataque_max=190, nivel=50,
      elemento='Sombrio', fraquezas=('Fogo', 'Eletrico'), resistencias=('Sombrio', 'Fisico'), chefe=True,
      exp_min=600, exp_max=800, moedas_min=500, moedas_max=700,
      drops_item=(('Fragmento do Arquiteto', 1.0),),
      descricoes_ataque=('O Arquiteto revela as engrenagens ocultas por trás da existência das dungeons',
                          'O Arquiteto dobra o espaço ao seu redor e ataca de todas as direções')),
}
