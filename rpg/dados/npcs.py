"""NPCs falantes do mundo aberto — Habusken, a estrada e Vethgard. As falas são
funções (não listas fixas) porque mudam conforme o progresso da história, sem
precisar de um sistema de diálogo à parte."""

from dataclasses import dataclass
from typing import Callable, List


@dataclass(frozen=True)
class Npc:
  nome: str
  falas: Callable[[object], List[str]]


def _falas_anciao_habusken(p):
  linhas = [
    'As dungeons sempre estiveram aqui, desde antes de eu nascer. Ninguém nunca soube dizer de onde vieram.',
    'Dizem que surgiram há 1800 anos. Um dia não existiam. No dia seguinte, existiam. Ninguém questiona isso há gerações.',
  ]
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


NPCS = {
  'anciao_habusken': Npc('Ancião de Habusken', _falas_anciao_habusken),
  'velho_caminhante': Npc('Velho Caminhante', _falas_velho_caminhante),
  'guarda_vethgard': Npc('Guarda de Vethgard', _falas_guarda_vethgard),
  'arquivista_sorel': Npc('Arquivista Sorel', _falas_arquivista_sorel),
  'orfao_mikel': Npc('Órfão Mikel', _falas_orfao_mikel),
}
