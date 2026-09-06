"""Constantes globais: cores de terminal, caminhos e parâmetros de balanceamento."""

import os
from pathlib import Path


class Cor:
  AZUL = '\033[1;34m'          # mana
  VERMELHO = '\033[1;31m'      # vida, dano, queimadura/sangramento/veneno, erros
  VERDE = '\033[1;32m'         # sucesso, cura, ganhos (exp/moedas), level up
  BRANCO = '\033[1;37m'        # ênfase neutra (nomes de habilidade, títulos)
  NEGRITO = '\033[;1m'
  AMARELO = '\033[1;93m'       # avisos, crítico, esquiva
  ROSA = '\033[1;95m'          # buffs, curandeira, guilda
  CIANO = '\033[1;36m'         # informação neutra
  CINZA = '\033[2;37m'
  RESET = '\033[0m'


# Fundo destacado usado para marcar a opção selecionada nos menus de seta.
DESTAQUE = '\033[7m'

def _diretorio_de_dados_do_usuario() -> Path:
  """Pasta padrão do sistema operacional pra guardar o save — não depende de
  onde o jogo foi executado (nem de rodar como .exe ou como script), então o
  save sobrevive a mover/reconstruir o executável e a trocar de pasta."""
  nome_pasta = 'RPGHabusken'
  if os.name == 'nt':
    base = os.environ.get('APPDATA') or str(Path.home())
  else:
    base = os.environ.get('XDG_DATA_HOME') or str(Path.home() / '.local' / 'share')
  return Path(base) / nome_pasta


DIRETORIO_BASE = _diretorio_de_dados_do_usuario()
ARQUIVO_SAVE = DIRETORIO_BASE / 'saves.json'
DIRETORIO_BACKUPS = DIRETORIO_BASE / 'backups'
NUMERO_DE_SLOTS = 3

# Balanceamento
CHANCE_CRITICO_BASE = 8          # em porcentagem — sem teto: empilhar sorte/acessório/
                                  # habilidade/especialização pode passar de 100%, virando crítico garantido.
MULTIPLICADOR_CRITICO = 1.6
MULTIPLICADOR_FRAQUEZA_ELEMENTAL = 1.5
MULTIPLICADOR_RESISTENCIA_ELEMENTAL = 0.5
FOME_MAXIMA = 10
FOME_CRITICA = 3

# Cada ponto de Poder soma esse tanto de dano percentual (junto com arma,
# Etén, raça etc. — tudo somado antes de aplicar sobre o dano base, ao invés
# de multiplicar em cadeia, que fazia o dano explodir rápido demais).
PODER_DANO_PERCENTUAL_POR_PONTO = 2
BONUS_ETEN_PERCENTUAL = 15
LIMITE_DEBUFF_PERCENTUAL = 80     # bônus percentual nunca deixa o dano cair abaixo de 20% do base

# Treinamento com o Mestre de Vethgard: diferente do Etén (bônus percentual
# recalculado a cada golpe), a "Disciplina" concede pontos de status fixos
# de uma vez só, na hora que o treinamento é concluído.
BONUS_DISCIPLINA_PODER = 15
BONUS_DISCIPLINA_SORTE = 15

# Roda elemental genérica: cada elemento é forte contra o próximo da lista e
# fraco contra o anterior — só entra em jogo quando o monstro NÃO já tem uma
# fraqueza/resistência explícita pro elemento do ataque (essas continuam
# valendo mais, com o multiplicador maior de cima).
CICLO_ELEMENTAL = ['Fisico', 'Fogo', 'Gelo', 'Eletrico', 'Agua', 'Sombrio']
MULTIPLICADOR_FRAQUEZA_CICLO = 1.25
MULTIPLICADOR_RESISTENCIA_CICLO = 0.8

# Monstro elite: variante mais forte de um monstro comum, sorteada na exploração.
CHANCE_MONSTRO_ELITE = 15          # 1 em N encontros de monstro comum vira elite
MULTIPLICADOR_ELITE_VIDA = 1.8
MULTIPLICADOR_ELITE_ATAQUE = 1.4
BONUS_ELITE_RECOMPENSA_PERCENTUAL = 100   # dobra exp/moedas e garante 1 drop extra

# Bônus só na PRIMEIRA vez que se derrota cada chefe — empilha com o bônus de
# elite se o chefe também rolar elite (não deveria acontecer na prática, mas
# a conta continua certa se acontecer).
BONUS_PRIMEIRO_ABATE_CHEFE_PERCENTUAL = 150

# Recurso de Fúria do Cavaleiro.
FURIA_CAVALEIRO_MAXIMA = 100
FURIA_GANHA_AO_ATACAR = 10
FURIA_GANHA_AO_LEVAR_DANO = 15

# Postura de combate.
BONUS_POSTURA_OFENSIVA_DANO = 10           # % a mais de dano causado
BONUS_POSTURA_OFENSIVA_DANO_RECEBIDO = 10  # % a mais de dano recebido
BONUS_POSTURA_DEFENSIVA_DANO = -10         # % a menos de dano causado (negativo)
BONUS_POSTURA_DEFENSIVA_REDUCAO = 15       # % a menos de dano recebido

# Reputação da guilda e encantamento de equipamento.
REPUTACAO_GANHA_POR_MISSAO = 10
ENCANTAMENTO_INCREMENTO = 3
ENCANTAMENTO_MAXIMO_ARMA = 30
ENCANTAMENTO_MAXIMO_ARMADURA = 20
ENCANTAMENTO_CUSTO_PRATA_BASE = 5   # multiplicado pelo tier atual — cada encantamento fica mais caro
ENCANTAMENTO_MATERIAL = 'Cristal Arcano'

# Loja rotativa: ofertas do dia, sorteadas com seed na data — todo mundo vê a
# mesma oferta no mesmo dia, e ela muda sozinha à meia-noite.
DESCONTO_OFERTA_DIA = 30
QUANTIDADE_OFERTAS_DIA = 3

# Reputação da guilda: cada tier libera missões melhores.
REPUTACAO_TIERS = [(0, 'Novato'), (100, 'Experiente'), (300, 'Veterano'), (600, 'Lendário')]

# Quadro de missões da guilda: um quadro por andar já visitado, com um número
# fixo de missões sorteadas, e um limite de missões equipadas ao mesmo tempo.
QUANTIDADE_MISSOES_POR_QUADRO = 3
MAX_MISSOES_ATIVAS = 2
CUSTO_RENOVAR_QUADRO = 100

# Auto-salvamento: silencioso, verificado nos loops principais (vila, dungeon,
# mundo aberto) — não interrompe o jogador, só evita perder progresso.
INTERVALO_AUTOSAVE_SEGUNDOS = 120

# Multiplicador único de experiência — se aplica a tudo (monstro, missão da
# guilda), pra deixar o nível subir mais rápido sem reescrever cada monstro.
MULTIPLICADOR_EXP_GLOBAL = 2.0

# Fome só desgasta 1 a cada N ações reais (batalha/exploração), em vez de
# toda vez — estava caindo rápido demais.
ACOES_POR_DESGASTE_FOME = 3

# Andar no mundo aberto desgasta fome por PASSO de verdade, bem mais frequente
# que "1 ação" de dungeon (que só desgasta ao pisar num ponto de interesse) —
# por isso usa um limiar bem maior, senão a fome zerava depois de poucos passos.
ACOES_POR_DESGASTE_FOME_MUNDO = 15

# Chance de qualquer efeito de status (habilidade do jogador, ataque de
# monstro, ou acessório) realmente grudar — nem todo golpe deveria garantir
# Queimadura/Paralisia/etc, senão vira injusto pra quem está do lado que apanha.
CHANCE_APLICAR_EFEITO_STATUS = 50   # em porcentagem

# Slots extras de acessório: começa com 1, cada compra libera mais um (até 3
# compras = 4 no total). Cada slot custa uma moeda de tier mais alto que o
# anterior — a moeda destrava dá o preço, e "fica cada vez mais caro" vem de
# subir de tier em vez de só aumentar o número.
CUSTOS_SLOT_ACESSORIO = [
  (500, 'moeda_cobre'),
  (50, 'moeda_prata'),
  (1, 'moeda_ouro'),
]
MAX_SLOTS_ACESSORIO = 1 + len(CUSTOS_SLOT_ACESSORIO)

# Níveis de perigo dos pontos de interesse de um andar (calculados pela
# distância até a entrada — sem precisar de dado extra por mapa). Só mudam a
# cor mostrada e o que se pode encontrar ali.
NIVEL_PERIGO_VERDE = 1
NIVEL_PERIGO_AMARELO = 2
NIVEL_PERIGO_VERMELHO = 3

# Slots extras de habilidade: começa com 3 (as iniciais da classe), cada
# compra libera mais um (até 2 compras = 5 no total).
CUSTOS_SLOT_HABILIDADE = [
  (300, 'moeda_cobre'),
  (30, 'moeda_prata'),
]
MAX_SLOTS_HABILIDADE = 3 + len(CUSTOS_SLOT_HABILIDADE)

# Foco do Arqueiro: recurso próprio, ganho ao atacar (mais se crítico),
# gasto em habilidades de "custo_foco" — paralelo à Fúria do Cavaleiro.
FOCO_ARQUEIRO_MAXIMO = 100
FOCO_GANHO_POR_ATAQUE = 8
FOCO_GANHO_POR_CRITICO_EXTRA = 12

# Marcar Alvo (Arqueiro): bônus percentual de dano que QUALQUER ataque
# recebe contra um alvo marcado — funciona como a Vulnerabilidade, só que
# aplicada por uma habilidade específica do Arqueiro.
MARCADO_BONUS_DANO_PERCENTUAL_PADRAO = 25

# Ressonância Arcana do Mago: cada vez que conjura um elemento DIFERENTE do
# último, ganha uma carga (até o máximo); repetir o mesmo elemento zera tudo.
RESSONANCIA_ARCANA_MAXIMA = 5
RESSONANCIA_ARCANA_BONUS_POR_STACK = 6   # % de dano por carga

# Atordoamento: bater na fraqueza elemental de um monstro enche uma barra;
# ao encher, ele fica atordoado (perde a próxima ação) — dá uma recompensa
# tática extra pra explorar fraquezas, além do multiplicador de dano.
ATORDOAMENTO_LIMIAR = 100
ATORDOAMENTO_GANHO_POR_ACERTO_FRACO = 25

# Fase de fúria de chefe (ver MonstroBase.tem_fase_furiosa): ativa uma vez,
# ao cair pra metade da vida, e aumenta o dano dele pelo resto da luta.
MULTIPLICADOR_FASE_FURIOSA_ATAQUE = 1.3

# Canalização: mini-jogo de memória opcional em habilidades "canalizáveis" —
# quanto mais símbolos acertar, maior o bônus de dano só no próximo golpe.
BONUS_CANALIZACAO_MAXIMO_PERCENTUAL = 60
SIMBOLOS_MINIGAME_CANALIZACAO = 4

# Grupos de monstros na exploração: só monstros comuns, nunca chefes.
CHANCE_GRUPO_MONSTROS = 4          # 1 em N encontros comuns vira grupo
TAMANHO_GRUPO_MONSTROS_MIN = 2
TAMANHO_GRUPO_MONSTROS_MAX = 3

# Mundo aberto (rpg/sistemas/mundo.py): mapas bem maiores que a tela, com uma
# "câmera" que mostra só uma janela ao redor do jogador — ela rola conforme
# ele anda, revelando mais do mapa aos poucos, em vez de mostrar tudo de uma
# vez feito as dungeons.
JANELA_MUNDO_LARGURA = 31
JANELA_MUNDO_ALTURA = 13

# Florestas do mundo aberto: cada passo numa célula de floresta tem 1 em N
# chance de um monstro selvagem aparecer.
CHANCE_ENCONTRO_SELVAGEM = 4

# Fome no mundo aberto desgasta por PASSO de verdade (não só ao interagir com
# algo), reaproveitando o mesmo limiar `ACOES_POR_DESGASTE_FOME` de dungeon.

# Diálogo de NPC: cada palavra da fala aparece uma de cada vez, com esse
# intervalo entre elas, pra dar impressão de que o NPC está falando de
# verdade — Enter/Espaço a qualquer momento pula pro texto completo.
VELOCIDADE_ANIMACAO_DIALOGO = 0.028
