"""Sidequests dadas por NPCs do mundo aberto — diferente das missões da
guilda (sorteadas num quadro, sempre "derrote N monstro"), cada sidequest é
uma missão narrativa fixa, ligada à história de um NPC específico."""

from dataclasses import dataclass
from typing import Optional

# tipo 'derrotar': derrote `quantidade` do monstro `alvo`.
# tipo 'entregar_item': entregue `quantidade` de `alvo` (chave de
#   personagem.itens_especiais — um item de sidequest, nunca da loja comum).
# tipo 'entregar_material': entregue `quantidade` de `alvo` (chave de
#   personagem.materiais — um material comum, de craft/drop).


@dataclass(frozen=True)
class Sidequest:
  id: str
  npc: str
  titulo: str
  descricao_oferta: str
  tipo: str
  alvo: str
  quantidade: int
  recompensa_exp: int
  recompensa_moedas: int
  texto_conclusao: str
  recompensa_material: Optional[str] = None


SIDEQUESTS = {
  'ecos_da_cantiga': Sidequest(
      id='ecos_da_cantiga', npc='velho_caminhante',
      titulo='Ecos da Cantiga',
      descricao_oferta=('A estrada anda perigosa demais pros viajantes, com tantos lobos rondando. '
                         'Derrote 5 deles pra mim, sim? Só quero que os viajantes cheguem inteiros.'),
      tipo='derrotar', alvo='Lobo', quantidade=5,
      recompensa_exp=200, recompensa_moedas=80,
      texto_conclusao=('Bom... muito bom. Talvez a próxima cantiga fale de estradas seguras, '
                        'pra variar.')),
  'lenco_da_familia': Sidequest(
      id='lenco_da_familia', npc='orfao_mikel',
      titulo='O Lenço da Família',
      descricao_oferta=('Minha família deixou cair um lenço na fuga pela estrada do norte. '
                         'Se alguém achar... eu pagaria o que tenho por ele.'),
      tipo='entregar_item', alvo='Lenço da Família de Mikel', quantidade=1,
      recompensa_exp=150, recompensa_moedas=100,
      texto_conclusao='Você... você achou. Obrigado. Isso é tudo que restou da minha mãe.'),
  'cristal_para_sorel': Sidequest(
      id='cristal_para_sorel', npc='arquivista_sorel',
      titulo='Um Cristal para os Registros',
      descricao_oferta=('Preciso de um Cristal Arcano pra estabilizar um pergaminho antigo antes '
                         'que ele se desfaça de vez. Sabe onde achar um?'),
      tipo='entregar_material', alvo='Cristal Arcano', quantidade=1,
      recompensa_exp=250, recompensa_moedas=50,
      texto_conclusao='Perfeito. Talvez agora eu consiga ler o que resta desse pergaminho...'),

  # Sidequests de Vethgard — recompensa bem maior, porque só dá pra chegar
  # aqui depois de limpar a dungeon inteira de Habusken (e o Selo provar
  # isso pro guarda da estrada).
  'ameaca_gelada': Sidequest(
      id='ameaca_gelada', npc='capita_wren',
      titulo='Ameaça Gelada',
      descricao_oferta=('A Torre Arcana anda mandando Elementais de Gelo até perto das muralhas. '
                         'Preciso de alguém forte pra abater 6 deles antes que cheguem aos portões.'),
      tipo='derrotar', alvo='Elemental de Gelo', quantidade=6,
      recompensa_exp=900, recompensa_moedas=450,
      texto_conclusao=('Vethgard te deve essa. A guarda vai dormir mais tranquila essa semana, '
                        'ao menos.')),
  'eco_do_abismo': Sidequest(
      id='eco_do_abismo', npc='estudioso_aldric',
      titulo='Eco do Abismo',
      descricao_oferta=('Estudo o que emerge do Abismo Submerso há anos. Uma Pérola Negra, intacta, '
                         'me diria mais sobre aquele lugar do que uma década de teoria. Traga-me uma?'),
      tipo='entregar_material', alvo='Pérola Negra', quantidade=1,
      recompensa_exp=1200, recompensa_moedas=600,
      texto_conclusao=('Extraordinário. A estrutura dela não é... natural. Isso muda tudo que eu '
                        'pensava saber sobre o Abismo.')),
}

SIDEQUESTS_POR_NPC = {}
for _sidequest in SIDEQUESTS.values():
  SIDEQUESTS_POR_NPC.setdefault(_sidequest.npc, []).append(_sidequest.id)
