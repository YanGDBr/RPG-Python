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
CHANCE_CRITICO_BASE = 8          # em porcentagem
CHANCE_CRITICO_MAXIMA = 60        # nunca passa disso, por mais que se empilhe sorte/acessório/habilidade
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

# Autobatalha: joga sozinho por N turnos usando sempre a habilidade disponível
# de maior dano previsto, cancelando cedo se a vida ficar baixa demais.
AUTOBATALHA_TURNOS = 5
AUTOBATALHA_VIDA_MINIMA_PERCENTUAL = 30

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
