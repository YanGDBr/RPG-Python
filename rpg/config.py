"""Constantes globais: cores de terminal, caminhos e parâmetros de balanceamento."""

import sys
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

if getattr(sys, 'frozen', False):
  # Rodando como .exe empacotado (PyInstaller): salvar ao lado do .exe, não
  # na pasta temporária onde o --onefile se descompacta a cada execução.
  DIRETORIO_BASE = Path(sys.executable).resolve().parent
else:
  DIRETORIO_BASE = Path(__file__).resolve().parent.parent

ARQUIVO_SAVE = DIRETORIO_BASE / 'contas.json'

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
