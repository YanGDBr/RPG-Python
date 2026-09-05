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
