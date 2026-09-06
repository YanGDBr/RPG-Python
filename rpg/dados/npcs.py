"""NPCs falantes do mundo aberto — Habusken, a estrada e Vethgard. As falas são
funções (não listas fixas) porque mudam conforme o progresso da história, sem
precisar de um sistema de diálogo à parte."""

import random
from dataclasses import dataclass
from typing import Callable, List

QUANTIDADE_FALAS_ALEATORIAS_POR_VISITA = 2


@dataclass(frozen=True)
class Npc:
  nome: str
  falas: Callable[[object], List[str]]


# O Ancião sempre abre com uma dessas duas linhas fixas de identidade, depois
# duas linhas sorteadas do poço abaixo — assim cada visita mostra uma
# combinação diferente, em vez do mesmo bloco de texto sempre igual.
_ANCIAO_LINHAS_ABERTURA = [
  'As dungeons sempre estiveram aqui, desde antes de eu nascer. Ninguém nunca soube dizer de onde vieram.',
  'Dizem que surgiram há 1800 anos. Um dia não existiam. No dia seguinte, existiam. Ninguém questiona isso há gerações.',
]

_ANCIAO_LINHAS_ALEATORIAS = [
  'Dizem que cada explorador vê a dungeon um pouco diferente lá dentro. Eu nunca desci pra conferir — não tenho mais idade pra essas coisas.',
  'Comida boa e descanso valem mais que qualquer poção, moço. Não economize lá em casa.',
  'Já vi gente forte demais pro próprio bem entrar numa dungeon e nunca mais voltar, de tanta pressa. Vá com calma nos primeiros andares.',
  'O ferreiro daqui é bom, mas caro. Ainda assim, todo encantamento vale — no fim das contas, é sua vida que tá em jogo.',
  'Soube que a guilda anda dando missão até pra quem já visitou andares mais fundos. Vale voltar lá de vez em quando.',
  'Um velho como eu não devia ter tanta história pra contar. Mas Habusken guarda mais segredos do que aparenta.',
  'Se um dia sentir o corpo fraco de fome, não hesite — comida é mais barata que a vida.',
  'Curioso, isso de Poder, Sorte, tudo que vocês aventureiros acumulam. Na minha época bastava um bom machado e um pouco de coragem.',
  'Vi muitos como você chegar aqui perdidos, sem lembrar do próprio nome direito. Sempre achei que isso significava algo maior.',
  'Habusken já foi bem maior do que é hoje. Ainda assim, continua sendo lar — pra quem escolhe ficar.',
  'Tem gente que troca de acessório toda hora, buscando a combinação perfeita. Eu digo: use o que funciona, e siga andando.',
  'Já enterrei mais amigos do que gostaria de contar. Cada um que volta vivo de uma dungeon é uma vitória, mesmo sem troféu nenhum.',
]


def _falas_anciao_habusken(p):
  linhas = [random.choice(_ANCIAO_LINHAS_ABERTURA)]
  linhas += random.sample(_ANCIAO_LINHAS_ALEATORIAS,
                           k=min(QUANTIDADE_FALAS_ALEATORIAS_POR_VISITA, len(_ANCIAO_LINHAS_ALEATORIAS)))
  if 'Dragão Ancião de Habusken' in p.chefes_derrotados:
    linhas.append('Você derrotou o Dragão Ancião? Poucos vivos podem dizer isso. Cuidado com o orgulho — ele também achava que tinha vencido tudo.')
  if p.cratera_vhalos_liberado and 'Vashtar, o Rei Cinza' not in p.chefes_derrotados:
    linhas.append('Se pretende seguir pra Cratera de Vhalos, procure o arquivo de Vethgard antes. Lá a memória é mais longa que a nossa.')
  if 'Vashtar, o Rei Cinza' in p.chefes_derrotados:
    linhas.append('A terra ao norte não está mais cinzenta, dizem os viajantes. Não sei o que você fez lá, mas Habusken te deve uma dívida que não sabe nomear.')
  return linhas


def _falas_velho_caminhante(p):
  linhas = [
    '(uma cantiga baixinho) "...o rei que venceu tudo, e perdeu pra si mesmo..."',
    'Ninguém mais lembra essa cantiga direito. Só sei que fala de um rei, e de uma coroa que não devia existir.',
  ]
  if 'Vashtar, o Rei Cinza' in p.chefes_derrotados:
    linhas.append('Ei... a cantiga mudou. Juro que mudou. Agora ela fala de um fim, não de um começo. Estranho, isso.')
  return linhas


def _falas_guarda_vethgard(p):
  linhas = [
    'Bem-vindo a Vethgard. Aqui a memória é mais longa — e mais pesada — do que em Habusken.',
    'Os mapas antigos marcam a Cratera de Vhalos só como "não ir". Ninguém nunca explicou o porquê. Só obedecemos.',
  ]
  if p.cratera_vhalos_liberado and 'Vashtar, o Rei Cinza' not in p.chefes_derrotados:
    linhas.append('Se já enfrentou tudo que Ilyrath tinha pra oferecer e ainda assim quer ir à Cratera... que os deuses, sejam eles quem forem, olhem por você.')
  if 'Vashtar, o Rei Cinza' in p.chefes_derrotados:
    linhas.append('Os batedores voltaram da estrada do norte. Disseram que o céu lá não está mais cinzento. Ninguém em Vethgard sabe o que fazer com essa notícia.')
  return linhas


def _falas_arquivista_sorel(p):
  linhas = [
    'Sou a guardiã do que sobrou dos registros antigos de Ilyrath. A maior parte se perdeu — ou foi apagada de propósito.',
    'Encontrei uma menção, num pergaminho meio carbonizado: "o rei que não devia ter vencido". Nunca entendi o que significa.',
  ]
  if p.cratera_vhalos_liberado and 'Vashtar, o Rei Cinza' not in p.chefes_derrotados:
    linhas.append('Se é da Cratera que você fala: tudo que sei é que quem desce lá não costuma voltar pra contar. Você seria o primeiro, até onde meus registros alcançam.')
  if 'Vashtar, o Rei Cinza' in p.chefes_derrotados:
    linhas.append('Você... voltou. Da Cratera. Vivo. Em vinte anos guardando este arquivo, nunca tive motivo pra escrever uma frase como essa.')
  return linhas


def _falas_orfao_mikel(p):
  if 'Vashtar, o Rei Cinza' in p.chefes_derrotados:
    return ['Alguém disse que a estrada do norte não está mais cinzenta. Foi você? Foi você que fez isso?']
  return [
    'Minha família fugiu da estrada do norte faz um mês. Diziam que a terra lá tinha ficado cinzenta. Sem cor nenhuma.',
    'Não gosto de falar sobre aquele lugar. Só queria que fosse embora.',
  ]


def _falas_capita_wren(p):
  linhas = [
    'Capitã da guarda de Vethgard. Se chegou até aqui a pé, com o Selo de Habusken em mãos, já provou que sabe se virar.',
    'A Torre Arcana fica logo depois das muralhas. Bonita de longe. De perto, é outra história.',
  ]
  if 'O Arquiteto' in p.chefes_derrotados:
    linhas.append('Soube que a Torre ficou em silêncio depois que você passou por lá. Bom silêncio, espero.')
  return linhas


def _falas_estudioso_aldric(p):
  linhas = [
    'Estudo o que o Abismo Submerso cospe de vez em quando na maré. A maioria não sobrevive à viagem até a superfície intacta.',
    'Vethgard vive de costas pro mar há gerações. Eu prefiro de frente — tem mais respostas lá do que em qualquer livro daqui.',
  ]
  if 'Kraken Ancestral' in p.chefes_derrotados:
    linhas.append('Você desceu até o Trono do Kraken? Daria anos da minha vida pra ver o que você viu lá embaixo.')
  return linhas


NPCS = {
  'anciao_habusken': Npc('Ancião de Habusken', _falas_anciao_habusken),
  'velho_caminhante': Npc('Velho Caminhante', _falas_velho_caminhante),
  'guarda_vethgard': Npc('Guarda de Vethgard', _falas_guarda_vethgard),
  'arquivista_sorel': Npc('Arquivista Sorel', _falas_arquivista_sorel),
  'orfao_mikel': Npc('Órfão Mikel', _falas_orfao_mikel),
  'capita_wren': Npc('Capitã Wren', _falas_capita_wren),
  'estudioso_aldric': Npc('Estudioso Aldric', _falas_estudioso_aldric),
}
