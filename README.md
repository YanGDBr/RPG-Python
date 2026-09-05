# RPG-Python

Esse foi um projeto que eu fiz quando era criança, eu fiz originalmente em um site antigamente que se chamava "replit" (atualmente o site mudou, e virou uma IA). Pois na época não tinha computador, então era o melhor lugar que eu encontrei para conseguir aprender a programar.

A branch `main` mantém o jogo como ele era, do jeito que eu fiz quando criança (só com os bugs que travavam o jogo corrigidos). A branch `update` é uma versão reestruturada e bem mais completa, com mais mecânicas e conteúdo.

## Para rodar o jogo

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

Ou, se já tiver Python instalado, só dar um duplo-clique em `jogar.bat` (ele cria
o ambiente e instala as dependências sozinho na primeira vez).

## Gerando um .exe independente

`jogar.bat` ainda precisa de Python instalado na máquina. Pra gerar um `.exe`
que roda sozinho em qualquer Windows, sem precisar instalar nada:

```
build_exe.bat
```

Isso gera `dist\RPG_Habusken.exe` — um único arquivo com o Python e todas as
dependências embutidos (~7 MB), roda sozinho. O save (`contas.json`) fica
salvo do lado do `.exe`. Cada nova versão do código precisa rodar o
`build_exe.bat` de novo pra gerar um `.exe` atualizado — o arquivo em si não é
versionado no git (é gerado, não é código-fonte).

## Estrutura (branch `update`)

O jogo foi reorganizado num pacote `rpg/`, por responsabilidade:

- `rpg/modelos/` — os dataclasses (personagem, monstro, item, habilidade)
- `rpg/dados/` — só dados de jogo (monstros, itens, habilidades, dungeons, receitas...), sem lógica
- `rpg/sistemas/` — a lógica de jogo (batalha, efeitos de status, exploração, economia, loja, cidade, crafting)
- `rpg/entrada.py` — leitura de teclado e o menu navegável por setas/WASD
- `rpg/jogo.py` — login/registro e o loop principal, que liga tudo

O save agora é em JSON (`contas.json`), não em pickle.

## Rodando os testes

```
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest tests/
```
