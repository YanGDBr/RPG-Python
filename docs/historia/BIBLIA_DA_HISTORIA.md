# Bíblia da História — RPG de Habusken

> Documento de referência narrativa. Não é código, não precisa ser implementado de
> uma vez — é o mapa completo da história, para ser construído aos poucos, arco por
> arco. Tudo aqui está aberto a ajuste; o que importa é manter a espinha dorsal:
> **um policial reencarnado que, ao se tornar forte demais, descobre que sua "segunda
> chance" sempre teve um preço, e no fim decide o que fazer com esse preço.**

---

## 0. Como usar este documento

Este arquivo tem três funções:

1. **Registrar a história completa**, do prólogo ao final, com nomes, motivações e
   a lógica por trás de cada reviravolta — para que qualquer sessão futura (eu ou
   você) possa reler e entender o "porquê" de cada peça sem precisar reconstruir do
   zero.
2. **Planejar como ela é revelada** — o jogo não deve narrar isso de uma vez. A
   seção 9 lista os mecanismos concretos de exposição (diálogos, itens, visões,
   arquivos, epílogos) e onde cada pedaço da verdade entra.
3. **Servir de roteiro de implementação** — a seção 10 quebra tudo em fases que dá
   pra ir entregando uma de cada vez, na ordem que faz mais sentido tecnicamente.

A história é dividida em **7 atos**. Os atos 0–2 acontecem no mundo local
(Ilyrath/Habusken, o que já existe no jogo). Os atos 3–6 são a expansão cósmica.
Nada do que já existe precisa ser jogado fora — pelo contrário, a seção 8 mostra
como cada chefe e dungeon atuais já se encaixam nessa história maior, só que
ninguém sabia disso ainda.

---

## 1. Filosofia da narrativa

- **Lenta e em camadas.** Nenhuma revelação grande acontece sem pelo menos uma
  pista plantada um ato antes. O jogador deve poder, numa segunda jogada, olhar
  pra trás e pensar "isso já estava ali, eu só não vi".
- **Ironia dramática, não picuinha.** O monólogo de abertura (seção 3.2) tem que
  funcionar perfeitamente bem numa primeira leitura inocente — e só ficar
  perturbador quando relido sabendo a verdade. Nada de personagem "piscando pro
  jogador" ou humor meta.
- **Ambiguidade real nas escolhas finais.** Os três finais (seção 7) não são
  "bem/neutro/mal" — são três respostas coerentes e defensáveis pra mesma pergunta
  (o que fazer com poder que não é seu). Cada um tem que doer um pouco.
- **Nomes únicos, nunca genéricos.** Nada de "O Líder", "O Deus da Vida" sem nome
  próprio. A lista completa está na seção 11 (Glossário/Dramatis Personae).
- **Transcendência é gradual.** O jogador sobe de nível dentro de Ilyrath, depois
  de patente dentro da Custódia, depois de entendimento sobre os Pilares. Cada
  camada é maior que a anterior, mas nenhuma aparece do nada.

---

## 2. Estrutura em atos (visão geral)

| Ato | Nome | Escala | Onde acontece |
|---|---|---|---|
| 0 | Prólogo — A Queda e o Convite | Humana | Terra (Brasil) → limbo |
| 1 | O Molde e o Mundo Novo | Pessoal → local | Ilyrath / Habusken |
| 2 | O Rei Cinza | Local (um reino) | Ilyrath |
| 3 | O Vértice | Multiversal | Fora do espaço-tempo |
| 4 | A Ascensão | Multiversal | Incontáveis mundos |
| 5 | Rachaduras | Multiversal | O Vértice, Arquivos |
| 6 | O Relicário | Cósmica | Fora da realidade |
| 7 | A Escolha | Cósmica/pessoal | — |

---

## 3. Ato 0 — Prólogo: A Queda e o Convite

### 3.1 A vida e a morte (expansão da história atual)

> Nota: do lado da Terra, a história fica deliberadamente vaga — sem nomes além
> do da cidade e da menina salva. Isso não é economia de escrita: é plot point.
> Ver 6.6 para o motivo.

O jogador era policial civil numa cidade pequena do interior, **Santa Rosa do
Almeida** — do tipo onde todo mundo conhece todo mundo. Seu último caso foi o
sequestro de **Bianca**, uma menina de oito anos, levada por um homem que a
cidade toda conhecia como "estranho, mas inofensivo" — até não ser mais. Ele a
encontrou no telhado do prédio mais alto da cidade, minutos depois do
sequestrador ameaçar, por telefone, jogá-la lá de cima.

Não teve negociação. Ele teve menos de dois segundos entre ver o movimento do
braço do sequestrador e agir — só se jogou pra puxar os dois de volta da mureta.
Conseguiu empurrar Bianca de volta pro telhado. Ele e o sequestrador caíram os
dois, dez andares.

Bianca sobreviveu. Ele morreu antes de chegar ao chão — ou melhor: **algo
decidiu que ele não precisava chegar ao chão**.

> Essa parte — o "algo decidiu" — é o gancho pro Ato 0.2. Na primeira jogada, o
> jogador não tem motivo pra estranhar essa frase. Na segunda, ela é a primeira
> pista de que a "reencarnação" não foi um milagre espontâneo — foi uma
> **intervenção observada e decidida por alguém**, no exato instante certo.

### 3.2 O Convite — monólogo de abertura

O jogador não desperta direto no corpo novo. Antes disso, existe um interlúdio —
um espaço sem chão, sem cima ou baixo, só uma voz. É aqui que "Deus" se apresenta.

Esse monólogo tem que ser lido duas vezes na cabeça de quem escreve: uma vez como
um jogador de primeira viagem, comovido e agradecido; outra vez sabendo que essa
figura é, na verdade, **Ordinael**, uma interface/avatar da organização cósmica
**A Custódia Infinita** (ver Ato 3), rodando um protocolo de recrutamento que já
tinha acontecido incontáveis vezes antes, em incontáveis mundos, com incontáveis
outros candidatos exatamente como ele. A segunda leitura deve doer.

**Rascunho do monólogo** (a ser adaptado no código, em `HISTORIA_INICIAL` /
`rpg/jogo.py`):

> *"Você não precisa ter medo. A dor já ficou pra trás — junto com o corpo, junto
> com o prédio, junto com o nome que os outros gritavam enquanto você caía.*
>
> *Eu vi o que você fez. Vi você escolher, num espaço de tempo pequeno demais pra
> chamar de escolha, salvar uma vida que não era a sua. Isso é raro. Mais raro do
> que você imagina. A maioria hesita — só um instante, só o suficiente. Você não
> hesitou.*
>
> *Por isso estou aqui. Chame-me do que quiser — Deus serve, se te dá conforto.
> Existem nomes mais antigos, mas nenhum vai significar nada pra você ainda.*
>
> *Eu não posso devolver o que você perdeu. Mas posso te dar algo novo: um corpo,
> um mundo, uma chance de viver sem o peso de tudo que veio antes. Existem formas
> diferentes de se começar de novo — cada uma com seus próprios dons, e seus
> próprios preços. Escolha o molde que mais soar como você.*
>
> *[seleção de raça]*
>
> *E dentro desse molde, existem caminhos — de força, de intelecto, de pontaria.
> Nenhum é superior. Todos serão testados.*
>
> *[seleção de classe]*
>
> *Uma última coisa, antes de te soltar nesse mundo: eu vou estar observando.
> Não por desconfiança — por cuidado. Quero ver o que você faz com essa segunda
> vida. Quero ver até onde ela te leva."*

Notas de escrita (o que faz esse texto funcionar nos dois sentidos):

- **"Eu vi o que você fez"** — soa como onisciência divina. Na verdade, é
  vigilância literal: a Custódia monitora limiares de sacrifício/coragem em
  incontáveis mundos como sinal de candidatos em potencial.
- **"Isso é raro"** — Ordinael não está comovido, está **catalogando**. A frase é
  quase um relatório de campo disfarçado de elogio.
- **"Existem formas diferentes de se começar de novo... cada uma com seus
  próprios dons e preços"** — a escolha de raça é literalmente descrita como um
  "molde", uma palavra técnica, de fabricação — não uma bênção. É a race-selection
  screen atual, sem mudar a mecânica, só a moldura.
- **"Eu vou estar observando... quero ver até onde ela te leva"** — na primeira
  leitura, é um pai orgulhoso torcendo pelo filho. Na segunda, é literalmente o
  objetivo da Custódia: descobrir o teto de poder de um candidato antes de
  recrutá-lo.

O jogo **nunca corrige essa leitura** até o Ato 5. Ordinael não aparece de novo
com frequência — talvez uma ou duas falas curtas e enigmáticas em marcos
específicos (ex: ao derrotar o primeiro chefe de cada dungeon, uma linha só, tipo
*"Continue."*), o suficiente pra lembrar o jogador que "Deus" está de olho, sem
gastar a carta cedo demais.

---

## 4. Ato 1 — O Molde e o Mundo Novo (Ilyrath)

O mundo onde o jogador acorda se chama **Ilyrath**. Habusken é a cidade natal do
personagem nesse mundo — o hub inicial que já existe no jogo. A história oficial
contada pelos NPCs de Habusken (e que é **verdadeira, só incompleta**) é a mesma
que já existe: dungeons surgiram há 1800 anos, de origem desconhecida, espalhadas
pelo mundo, e enfrentá-las é como aventureiros ganham poder e reconhecimento.

O que ninguém em Ilyrath sabe (e o jogador só vai entender no Ato 5): essas
dungeons não são fenômenos naturais. Elas foram **semeadas** pela Custódia
Infinita como campos de teste — não só em Ilyrath, mas em incontáveis mundos
simultaneamente. Ilyrath é só um lote de uma colheita muito maior. 1800 anos atrás
não foi um evento cósmico aleatório: foi quando a Custódia "plantou" esse mundo
específico no seu programa de cultivo de candidatos.

Isso não muda nada da jogabilidade atual — é uma **camada de leitura por baixo**
do que já existe. Ver seção 8 para o encaixe exato de cada dungeon/chefe atual
nessa cronologia.

---

## 5. Ato 2 — O Rei Cinza

### 5.1 Vashtar

Depois de Habusken, Torre Arcana e Abismo Submerso (o conteúdo atual do jogo), o
mundo de Ilyrath tem um problema final, maior que qualquer um dos anteriores:
**Vashtar, o Rei Cinza**, autoproclamado Rei Demônio, que desperta na
**Cratera de Vhalos** — uma ferida antiga na terra, ao norte de Habusken, que os
mapas antigos marcam só como "não ir".

Vashtar não é um demônio "nascido" das dungeons como os outros monstros — ele era,
mil e duzentos anos atrás, um dos primeiros campeões a atravessar todas as
dungeons de Ilyrath, exatamente como o jogador está fazendo agora. Ele venceu.
E então, no fundo da Cratera de Vhalos (não uma dungeon oficial — algo mais
antigo, mais profundo, deliberadamente escondido embaixo de tudo), ele encontrou
um **fragmento** — um cristal negro, pulsante, do tamanho de um punho, que os
registros de Habusken sequer mencionam porque quem os escreveu nunca soube que
existia.

Esse fragmento é uma **lasca de Thanoril**, o Pilar da Morte (ver Ato 6) — um
pedaço microscópico, arrancado à força do Pilar inteiro há muito tempo e
escondido em Ilyrath pela Custódia como **isca**: um teste de ressonância, pra ver
se algum candidato daquele mundo seria capaz de tocar poder divino sem se
corromper.

Vashtar não foi capaz. O fragmento o consumiu por dentro ao longo de gerações —
ele não envelheceu, não morreu, só foi ficando **menos ele e mais outra coisa**,
até virar o "Rei Demônio" que a lenda de Ilyrath conhece hoje: um tirano que
governa um exército de corrompidos saídos da própria Cratera, alimentado por um
poder que não devia estar ali.

### 5.2 A batalha e a consequência

O confronto com Vashtar é o clímax de Ilyrath — mecanicamente, o chefe final
"de verdade" do mundo local, mais forte que qualquer chefe de dungeon atual.
Narrativamente, matá-lo faz duas coisas ao mesmo tempo:

1. **Liberta Ilyrath** da ameaça — final "local" satisfatório, se o jogador
   quisesse parar por aí.
2. **Estilhaça o fragmento de Thanoril** que Vashtar carregava. Esse estilhaçar
   solta, por uma fração de segundo, um sinal de energia que atravessa a
   realidade — exatamente o tipo de assinatura que a Custódia monitora há
   séculos, esperando.

É esse sinal, e não a mera existência do jogador, que finalmente convoca
Ordinael de volta — dessa vez não como uma voz num limbo, mas em pessoa (ou o
mais perto disso que Ordinael consegue chegar), com uma proposta muito mais
concreta que a do início do jogo.

> Gancho de escrita: a queda de Vashtar deveria vir acompanhada de uma cutscene
> curta onde o cristal se rompe e, por um instante, o jogador "sente" algo — a
> mesma sensação que vai reconhecer, muito mais tarde, como a presença de um
> Pilar (ver 8.3). Não precisa ser explicado. Só uma linha, tipo: *"Por um
> segundo, e só um segundo, você sentiu como se alguém — ou algo — enorme
   tivesse aberto os olhos em algum lugar muito, muito longe."*

---

## 6. Ato 3 — O Vértice

### 6.1 A Custódia Infinita

**A Custódia Infinita** se apresenta ao jogador como exatamente o que o nome
sugere: uma organização antiga, benevolente, dedicada a **proteger a realidade**.
Eles zelam por incontáveis mundos, respondem a ameaças que nenhum reino sozinho
conseguiria enfrentar, e recrutam os mais fortes de cada mundo pra ajudar nessa
missão. Todo mundo que o jogador conhece na Custódia é, à primeira vista,
genuinamente gentil. Isso não é encenação — a maioria deles **acredita** no que
fazem. É isso que torna a verdade, mais tarde, mais difícil de engolir: não tem
vilão torcendo o bigode em nenhuma sala, só gente boa fazendo parte de uma coisa
que não questiona.

O nome tem duplo sentido, plantado desde o início pra quem prestar atenção:
"custódia" é também **prisão sob guarda**. A organização que promete proteger a
realidade é, literalmente, quem mantém os Pilares (ver Ato 6) presos.

### 6.2 O Vértice

**O Vértice** é o hub cósmico da Custódia — não um lugar no espaço, mas uma
"dobra" fora dele, moldada como uma cidade-fortaleza flutuante entre estrelas que
não existem em céu nenhum. É pra onde o jogador é levado depois de Vashtar, e vira
o hub central do Ato 3 em diante — equivalente cósmico da vila de Habusken, com
NPCs, lojas (agora vendendo tecnologia/magia de nível estelar) e a árvore de
patentes.

### 6.3 Patentes

O jogador sobe de patente completando missões — mecanicamente parecido com o
sistema de reputação de guilda que já existe, só que em escala muito maior, com
seis níveis:

1. **Aspirante** — missões de resgate puras. Salvar colônias, curar pragas,
   proteger caravanas espaciais. Tudo genuinamente heroico. A primeiríssima
   missão do jogador nessa patente é pessoal — ver 6.6.
2. **Errante** — combate itinerante entre mundos. Caçar ameaças que atravessam
   fronteiras entre realidades.
3. **Guardião** — conter "Corrompidos": anomalias de realidade que a Custódia
   trata como pragas perigosas (e que, mais tarde, o jogador vai suspeitar que
   às vezes são só... vítimas de outra coisa).
4. **Arauto** — primeira patente onde as missões começam a incomodar. Missões de
   "coleta de Eco Residual": extrair energia de mundos condenados/moribundos
   antes que "se percam". Tecnicamente indolor. Ainda assim, algo nisso é
   estranho — por que a Custódia sempre sabe, com tanta antecedência, que um
   mundo vai morrer?
5. **Censor** — missões de silenciamento. Localizar e "reeducar" (ou pior)
   expedições que descobriram fragmentos demais da verdade. É aqui que o
   jogador conhece Nyra Voss (seção 6.6).
6. **Sumo-Custódio** — acesso pleno aos Arquivos Absolutos, ao Relicário, e à
   sala de decisão dos líderes. Última patente antes do Ato 7.

### 6.4 Missões de exemplo (uma por patente, pra dar o tom)

- *Aspirante* — "Evacue os últimos moradores de Vethmoor Baixo antes que o
  colapso estelar consuma o setor."
- *Errante* — "O Devorador de Luas se aproxima do sistema de Kaross. Detenha-o
  antes que ele chegue à terceira lua habitada."
- *Guardião* — "Uma anomalia — um Corrompido — foi avistada se replicando no
  distrito industrial de Ossuen. Contenha-a antes da propagação."
- *Arauto* — "O planeta Ishtel-9 entrará em colapso em quatro ciclos. Extraia o
  Eco Residual antes da perda total."
- *Censor* — "A expedição Rhoswen ultrapassou os limites do Setor 7 e acessou
  registros classificados. Localize os sobreviventes."
- *Sumo-Custódio* — "Avalie a viabilidade de extração direta do espécime
  contido na Ala IV do Relicário." (primeira vez que a palavra "espécime" é
  usada pra descrever um Pilar — e o jogador, a essa altura, já sabe o
  suficiente pra sentir o estômago revirar.)

### 6.5 A Primeira Missão — Retorno à Terra

A ficha de missão que Selvarin entrega ao jogador recém-promovido a Aspirante não
diz "Terra". Diz **"Sol-3 — Anexo Ínfimo 12"**, uma linha perdida entre milhares
de outras num catálogo que a Custódia nem considera prioritário. É só quando o
jogador atravessa a fenda de trânsito e reconhece o formato das nuvens, o cheiro
de terra molhada, a língua que as pessoas ao redor falam, que entende: é lá. É
casa.

Ninguém na Custódia sabe disso, nem pergunta. Pra eles é só mais um mundo de
catálogo baixo com uma incursão pra conter. Esse contraste — a burocracia fria de
um lado, o soco no estômago pessoal do outro — é o coração da cena, e deve ficar
implícito, nunca dito em voz alta pelo jogador.

**A ameaça:** uma célula de reconhecimento do **Enxame Kryvex**, um coletivo
alienígena que não invade — *coleta*. Pousaram perto de Santa Rosa do Almeida
poucos dias antes (do ponto de vista da Terra) pra escanear e extrair material
biológico/energético antes de ir embora, sem cerimônia, sem declaração de guerra.
Não é uma invasão em escala global — é um incidente regional, contido, do tipo
que os noticiários de fora tratam como "evento atmosférico raro" ou simplesmente
não noticiam. Ninguém em Santa Rosa do Almeida vai saber, depois, que aquilo foi
um primeiro contato de verdade.

**A discrepância de tempo:** ao consultar um jornal ou terminal local pra se
situar, o jogador descobre que se passaram **cerca de 25 anos** desde a queda do
prédio — muito mais do que os poucos anos que ele parece ter vivido em Ilyrath e
na antecâmara do Vértice. Isso nunca é explicado nesse momento. É só um mal-estar
que fica. (Gancho: a explicação real — ou pelo menos a primeira pista dela — só
vem muito depois, na Impressão de Vaelirn, seção 8.3.)

**O véu:** todo operativo da Custódia enviado a mundos de baixa magia/tecnologia
recebe um "véu de trânsito" — um disfarce passivo que o faz passar por um humano
comum aos olhos dos nativos. O véu não reconstrói o rosto antigo do jogador; gera
um rosto novo, diferente, sempre. Ou seja: mesmo sem os 25 anos, mesmo com um
corpo novo escolhido lá no Ato 0, nunca ia haver rosto nenhum pra Bianca
reconhecer.

**O reencontro:** enquanto neutraliza a célula do Enxame e ajuda a evacuar o
centro da cidade — incluindo o quarteirão do antigo "prédio dos Correios", hoje
reformado num pequeno arquivo municipal —, o jogador cruza com uma mulher de
trinta e poucos anos. É Bianca. Ela dedica boa parte da vida adulta a uma rede de
apoio a famílias de crianças desaparecidas, algo que começou a montar sozinha,
sem formação nenhuma pra isso, só porque sabia exatamente o que essas famílias
sentiam. Uma vez por ano, sempre na mesma data, ela visita o prédio reformado e
fica um tempo parada na calçada — o único ritual que mantém pra marcar o dia em
que um homem sem nome (o caso nunca foi resolvido publicamente; ele morreu sem
identificação clara, e ela era nova demais pra reter detalhes) morreu salvando a
vida dela.

O jogador tem a chance de se revelar e não tem como — não literalmente: não tem
nome antigo pra dar, o véu não deixa o rosto antigo aparecer, e existe uma norma
não-oficial da Custódia (mencionada por Selvarin de forma quase casual, nunca
como ordem direta) de que recrutas não devem "reestabelecer vínculos
desnecessários com vestígios da vida anterior" — apresentada como cuidado
("é mais saudável seguir em frente"), mas que serve, na prática, aos interesses
da Custódia de manter seus operativos sem raízes. O jogador pode escolher, nesse
momento, entre:

1. Simplesmente ajudá-la a evacuar sem dizer nada — salvando a vida dela pela
   segunda vez, de novo em anonimato completo, fechando o ciclo em silêncio.
2. Quebrar o protocolo o suficiente pra dizer uma coisa pequena e específica —
   um detalhe daquele dia que só quem estava lá no telhado poderia saber — antes
   de sumir de volta pela fenda. Não é uma confissão, não prova nada que ela possa
   repetir pra alguém. Mas é o suficiente pra, pela primeira vez em vinte e cinco
   anos, ela ter certeza absoluta de uma coisa: **ele foi real, e de alguma forma,
   ainda está por aí.**

A opção 2 é a recomendada pra levar adiante — é o beat "mais complexo" que dá
peso emocional real ao retorno, sem quebrar a regra de que o jogador nunca revela
quem foi antes. Bianca pode (e deveria) reaparecer brevemente nos epílogos dos
três finais (seção 9) — uma cena curta mostrando como a escolha cósmica do
jogador ecoa de volta pra essa vida humana específica que ele deixou pra trás.

> Nota em aberto, de propósito: por que a primeira missão de um Aspirante
> recém-chegado cai justo no mundo de origem dele? Selvarin comenta, quase
> de passagem, que "a primeira missão costuma ser... reveladora" — sem nunca
> explicar o que quer dizer com isso. Pode ser coincidência de detecção de
> ameaça. Pode ser um teste deliberado, pra ver se o recruta ainda carrega apego
> demais ao que deixou pra trás. O jogo nunca resolve qual das duas é verdade.

### 6.6 Personagens do Vértice

- **Selvarin** — o mentor que recebe o jogador na chegada. Genuinamente gentil,
  paciente, órgulhoso do progresso do jogador. Sabe mais do que aparenta, mas
  escolheu, há muito tempo, não questionar — é mais fácil viver assim. Não é
  vilão nem herói: é o retrato de "eu só cumpro meu trabalho" levado a sério.
- **Iskar Voth** — rival de patente, competitivo, sempre um passo à frente ou
  atrás do jogador. Representa o caminho que aceita tudo sem perguntar — motivado
  puramente por ambição. Pode ser usado, dependendo de como a história crescer no
  jogo, como um contraponto trágico: alguém que chega à Sumo-Custódia
  rápido demais, sem nunca ter parado pra duvidar.
- **Nyra Voss** — ex-Censora fugitiva. Na sua última missão de silenciamento, não
  conseguiu completar a ordem — os "sobreviventes" que deveria neutralizar eram
  uma família inteira, e o que eles tinham descoberto era verdade. Ela desertou,
  virou fugitiva, e é quem, no Ato 5, entrega ao jogador o primeiro fio real da
  verdade sobre o Relicário.

---

## 7. Ato 5 — Rachaduras na Verdade

Esse é o ato "de investigação" — o jogador já é forte, já subiu patentes, e
começa a notar inconsistências pequenas antes de qualquer revelação explícita:

- Um Arauto reclama, em conversa de corredor, que um mundo "programado" pra
  colapsar não deveria ter durado tanto — como se o colapso não fosse natural,
  mas **agendado**.
- Arquivos de missões antigas (acessíveis conforme o jogador sobe de patente)
  têm nomes de mundos repetidos ano após ano, sempre "prestes a morrer" — mundos
  que nunca terminam de morrer, só continuam sendo "colhidos".
- Um contato anônimo (Nyra, ainda sem se identificar) começa a deixar mensagens
  em terminais que o jogador usa — nada explícito, só perguntas: *"Você já se
  perguntou por que a Custódia sempre sabe onde e quando?"*

O encontro direto com Nyra Voss acontece perto do fim do Ato 5: ela conta o que
sabe (sem saber tudo) — que existe um cofre, oculto de quase toda a Custódia,
chamado **O Relicário**, e que dentro dele não tem "espécimes" nem "anomalias".
Tem **prisioneiros**.

---

## 8. Ato 6 — O Relicário e os Quatro Pilares

### 8.1 O que são os Pilares

Os Pilares não são personagens no sentido comum — são **fundamentos da
realidade**, mais parecidos com leis físicas manifestas do que com deuses que
falam ou pensam como gente. Existem quatro:

- **Yssara** — Pilar da Vida.
- **Vaelirn** — Pilar do Tempo.
- **Kaeldris** — Pilar do Espaço.
- **Thanoril** — Pilar da Morte.

Nenhum deles fala. Nenhum deles tem vontade no sentido de "querer" algo do jeito
que uma pessoa quer. Quando o jogador se aproxima o suficiente de um deles (ou de
um fragmento, como o de Vashtar), a "comunicação" acontece por **impressão
direta** — o jogador simplesmente sabe, sente, entende, sem nenhuma palavra
trocada. Isso deve ser escrito em prosa sensorial, nunca como diálogo.

A Custódia Infinita os aprisionou há eras — o motivo oficial (o que os líderes
acreditam, ou dizem acreditar) é que quatro forças absolutas soltas e sem
supervisão são incompatíveis com uma realidade estável: a vida sem controle vira
praga; o tempo sem controle vira paradoxo; o espaço sem controle vira colapso; a
morte sem controle apaga tudo. Prendê-los, argumentam, é o preço de manter o
multiverso funcionando. Isso não é mentira — é meia-verdade, a pior espécie: o
suficiente de razão pra doer na hora do jogador decidir o que fazer no Ato 7.

### 8.2 O Relicário

O Relicário existe fora da realidade normal — nem espaço nem não-espaço, uma
"sala de estar" reservada apenas para Sumo-Custódios (e agora o jogador). Cada
Pilar é mantido numa "Ala" separada, cada uma com sua própria lógica visual —
um design sugerido:

- **Ala I — Yssara (Vida):** um jardim que nunca para de crescer e nunca
  floresce; tudo em brotos eternos.
- **Ala II — Vaelirn (Tempo):** um relógio sem ponteiros, onde o mesmo instante
  se repete e nunca avança nem volta.
- **Ala III — Kaeldris (Espaço):** uma sala do tamanho de um quarto que, se
  você andar por tempo suficiente, some no horizonte — infinita e minúscula ao
  mesmo tempo.
- **Ala IV — Thanoril (Morte):** um silêncio absoluto, sem eco, onde nem o som
  dos próprios passos do jogador se ouve.

### 8.3 As impressões (rascunho de texto para cada Pilar)

Trechos de exemplo de como cada "comunicação" pode ser escrita — sem diálogo,
em segunda pessoa, sensorial:

> **Yssara:** *Você não ouve nada. Não sente frio nem calor. Mas por um instante,
> sente o que é ser semente, broto, raiz e fruto ao mesmo tempo — e sente, junto,
> o cansaço de séculos sendo isso tudo sem nunca poder simplesmente florescer e
> acabar.*

> **Vaelirn:** *Não existe "antes" nem "depois" aqui dentro. Você entende, sem
> saber como entendeu, que já esteve nesse mesmo lugar antes — e vai estar de
> novo — e que "antes" e "de novo" não significam nada pra quem está preso do
> lado de dentro do relógio.*
>
> *E, por baixo disso, uma segunda certeza, pequena e fria: você entende, sem
> nenhuma palavra, por que aquele retorno à Terra pareceu ter avançado rápido
> demais. Vaelirn não fez isso — só é o tipo de coisa que só faz sentido perto
> de algo assim.*

> **Kaeldris:** *A sala é do tamanho de um quarto. A sala não tem fim. As duas
> coisas são verdade ao mesmo tempo, e por um segundo você entende que "tamanho"
> nunca foi uma pergunta que fizesse sentido pra perguntar.*

> **Thanoril:** *Não tem medo aqui. Não tem dor. Só a ausência total de qualquer
> coisa que precise continuar — e, por baixo disso, algo que não é bem alívio,
> mas é parecido.*

---

## 9. Ato 7 — A Escolha

Depois do Relicário, o jogo apresenta três caminhos — não como uma escolha de
menu simples, mas como o acúmulo natural de tudo que o jogador fez até ali
(patente alcançada, missões aceitas ou recusadas, se ajudou ou ignorou Nyra,
quanto poder acumulou). Os três finais:

### Final A — "O Novo Grão-Custódio"

O jogador aceita a proposta de **Théris Kalanor**, o Grão-Custódio que lidera o
programa de extração, e assume um assento entre os líderes. Não é apresentado
como fracasso — é apresentado como o caminho de quem, depois de ver tudo, decide
que é melhor ter uma cadeira na mesa do que deixar outra pessoa decidir sozinha.
O epílogo deve ser desconfortável, não triunfante: o jogador virou exatamente o
tipo de figura que odiava no início do Ato 4, só que agora com os motivos "certos".

### Final B — "Os Pilares Libertos"

O jogador rompe os selos e liberta Yssara, Vaelirn, Kaeldris e Thanoril de volta
à realidade. É o final "heróico" mais óbvio, mas não deve ser limpo: quatro
forças absolutas soltas de uma vez alteram a realidade de formas imprevisíveis —
mundos inteiros mudam, alguns para melhor, outros de um jeito que ninguém pediu.
A liberdade tem custo, mesmo quando é a coisa certa a se fazer.

### Final C — "A Ascensão Proibida" (o mais difícil)

Em vez de libertar os Pilares para o mundo, o jogador os **absorve** — os quatro,
um de cada vez, cada absorção sendo, mecanicamente, o conteúdo mais difícil do
jogo (um "chefe" ou desafio por Pilar). O resultado não é o jogador "ficando mais
forte" no sentido comum — é o jogador deixando de ser inteiramente humano,
fundindo-se com Vida, Tempo, Espaço e Morte ao mesmo tempo, tornando-se, na
prática, um **quinto Pilar**. O epílogo desse final deve ser escrito de forma
deliberadamente diferente dos outros dois — menos pessoal, mais distante, como se
quem estivesse narrando não fosse mais exatamente "alguém".

### Coda pessoal (sugestão para os três epílogos)

Cada um dos três epílogos deveria fechar com uma cena curta, de poucas linhas,
voltando a **Bianca** (seção 6.5) — não pra explicar nada a ela, ela nunca vai
entender a escala cósmica do que aconteceu, mas pra mostrar que a escolha do
jogador ecoa de volta até a única vida humana concreta que ele deixou pra trás.
No Final A, talvez ela simplesmente continue a vida dela, sem saber que o mundo
mudou de mãos. No Final B, talvez ela sinta, sem entender por quê, que algo no ar
mudou. No Final C, talvez ela seja a última coisa "humana" que o jogador ainda
reconhece antes de deixar de ser inteiramente alguém.

---

## 10. Como o conteúdo atual do jogo já se encaixa nisso

Nada precisa ser reescrito — só reinterpretado:

- **Dungeon de Habusken (Andares 1–5) e Torre Arcana** — trials mundanos de
  cultivo. Fazem parte da "colheita" de Ilyrath sem que ninguém saiba.
- **O Arquiteto** (chefe final da Torre Arcana) — já tem a fala *"O Arquiteto
  revela as engrenagens ocultas por trás da existência das dungeons"*. Isso passa
  a ser lido literalmente: O Arquiteto era (ou é uma cópia/eco de) um construto
  da Custódia responsável por manter o ciclo de testes de Ilyrath funcionando. Ele
  já estava tentando dizer a verdade — só que ninguém, incluindo o jogador na
  hora, tinha contexto pra entender.
- **Abismo Submerso / Kraken Ancestral** — o Abismo esconde um eco selado de
  **Yssara** (Vida), colocado ali pela Custódia como um dos incontáveis "postos de
  teste de ressonância" espalhados pelo multiverso — o mesmo princípio do
  fragmento de Thanoril que corrompeu Vashtar, só que com um resultado diferente
  (o Kraken não foi corrompido — foi só um guardião natural que cresceu forte
  demais perto do eco).
- **Vashtar** (novo, seção 5) — o gatilho que conecta Ilyrath ao resto da história.

---

## 11. O Mundo Aberto (visão de implementação futura)

Pra história ser descoberta aos poucos (não só narrada em bloco), o jogo precisa
de um espaço pra isso — algo parecido com as dungeons atuais (mapa ASCII,
movimento por WASD/setas), só que sem combate obrigatório e com NPCs conversáveis.
Sugestão de estrutura:

- **Mapa geral de Ilyrath**: conecta Habusken a 1–2 cidades novas (sugestão:
  **Vethgard**, mais próxima da Cratera de Vhalos, com um arquivo/biblioteca
  antiga) por estradas navegáveis, no mesmo estilo dos mapas de dungeon (paredes,
  pontos de interesse `?`), mas os pontos de interesse aqui abrem diálogo em vez
  de batalha.
- **NPCs com árvore de diálogo simples**: 2–4 falas por NPC, uma das quais muda
  depois de marcos da história (ex: antes/depois de matar Vashtar).
- **"Notas" e "Diários"**: itens de leitura (sem função de jogo, só lore) que
  podem ser encontrados nas dungeons já existentes — pequenos textos que, relidos
  depois do Ato 5, ganham sentido novo.
- **O Vértice** (Ato 3 em diante) usa a mesma engine de mapa aberto, só que com
  visual "cósmico" e NPCs de patente.

---

## 12. Mecanismos concretos de exposição da história

Lista de "onde" cada verdade entra, prática o suficiente pra virar tarefa de
implementação:

1. **Monólogo de abertura** (Ato 0) — obrigatório, já existe como
   `HISTORIA_INICIAL`, precisa reescrita (rascunho pronto na seção 3.2).
2. **Falas curtas e raras de Ordinael** em marcos (primeiro chefe de cada
   dungeon) — uma linha só, nunca mais.
3. **Diálogo ambiente em Habusken/Vethgard** — NPCs comentando o mundo, sem
   saber de nada.
4. **Cutscene de Vashtar** (seção 5.2) — a "sensação" que planta o gancho pro
   Ato 3.
5. **Descrição de itens/materiais** — os já existentes (Núcleo do Dragão
   Ancião, Fragmento do Arquiteto, Tinta de Kraken etc.) podem ganhar uma
   segunda camada de descrição, desbloqueada só depois do Ato 5.
6. **Diários/Notas** encontráveis nas dungeons (seção 11).
7. **Diálogo de patente** no Vértice — cada promoção vem com uma fala curta de
   Selvarin ou de outro Sumo-Custódio.
8. **Arquivos Absolutos** — um "codex" que desbloqueia entradas conforme o
   jogador sobe de patente e completa missões específicas.
9. **Mensagens de Nyra Voss** — terminal/mural que só aparece a partir do meio
   do Ato 4, com mensagens cada vez mais diretas.
10. **A Missão de Sol-3 / Retorno à Terra** (seção 6.5) — a primeira missão de
    Aspirante planta, ao mesmo tempo, a discrepância de tempo (paga só na
    Impressão de Vaelirn) e o fio pessoal com Bianca (pago nos epílogos).
11. **As Impressões dos Pilares** (seção 8.3) — o clímax de exposição, no
    Relicário.
12. **Epílogos** — um texto por final (Ato 7), cada um com tom de escrita
    distinto, fechando com a coda pessoal de Bianca.

---

## 13. Cronologia oculta (para referência interna)

Ordem real dos eventos, do mais antigo ao mais recente (o jogador nunca vê isso
como uma linha do tempo explícita — ela existe pra manter consistência):

1. Há eras — A Custódia Infinita prende Yssara, Vaelirn, Kaeldris e Thanoril no
   Relicário.
2. Há muito tempo (pré-Ilyrath) — a Custódia começa a semear dungeons em
   incontáveis mundos como programa de cultivo/teste de candidatos.
3. **1800 anos atrás** — Ilyrath é "plantado" no programa; as dungeons de
   Habusken e da Torre Arcana surgem.
4. **~1200 anos atrás** — Vashtar, então um aventureiro comum, atravessa todas
   as dungeons de Ilyrath e encontra o fragmento de Thanoril na Cratera de
   Vhalos. Começa a se corromper.
5. Séculos de reinado de Vashtar como Rei Cinza (o "presente" de Ilyrath antes
   do jogo começar).
6. **Presente do jogo** — o jogador morre em Santa Rosa do Almeida e é
   reencarnado por Ordinael (Ato 0). Percorre Habusken, Torre Arcana, Abismo
   Submerso (Ato 1). Derrota Vashtar (Ato 2) — o fragmento se rompe, sinal
   detectado pela Custódia.
7. Ordinael recruta o jogador para a Custódia Infinita (Ato 3).
8. **Primeira missão de Aspirante**: retorno a Sol-3 (Terra), 25 anos depois da
   queda — contenção do Enxame Kryvex e reencontro com Bianca (seção 6.5).
9. O jogador sobe de patente ao longo de incontáveis missões em outros mundos
   (Ato 4).
10. O jogador descobre Nyra Voss e a verdade sobre o Relicário (Ato 5).
11. O jogador entra no Relicário e sente os quatro Pilares (Ato 6) — e entende,
    de relance, a razão da discrepância de tempo na Terra.
12. Escolha final (Ato 7).

---

## 14. Dramatis Personae / Glossário

| Nome | Papel |
|---|---|
| **Bianca** | A menina salva pelo jogador em Santa Rosa do Almeida — reencontrada 25 anos depois na missão de Sol-3 (seção 6.5), já adulta. |
| **Ordinael** | "Deus" da abertura — na verdade, avatar/interface da Custódia Infinita. |
| **A Custódia Infinita** | A organização cósmica — se apresenta como protetora, na verdade aprisiona os Pilares. |
| **O Vértice** | Hub cósmico/fortaleza da Custódia, fora do espaço normal. |
| **Selvarin** | Mentor gentil do jogador dentro da Custódia. |
| **Iskar Voth** | Rival de patente, ambicioso, nunca questiona. |
| **Nyra Voss** | Ex-Censora fugitiva, primeira a revelar a verdade ao jogador. |
| **Théris Kalanor** | Grão-Custódio, líder do programa de extração dos Pilares — antagonista central do Ato 6–7. |
| **Vashtar, o Rei Cinza** | Rei Demônio de Ilyrath, corrompido por um fragmento de Thanoril. |
| **Yssara** | Pilar da Vida. |
| **Vaelirn** | Pilar do Tempo. |
| **Kaeldris** | Pilar do Espaço. |
| **Thanoril** | Pilar da Morte. |
| **O Relicário** | Prisão extradimensional dos quatro Pilares. |
| **Ilyrath** | O mundo de fantasia onde o jogador reencarna (contém Habusken). |
| **Habusken** | Cidade natal do personagem em Ilyrath (já existente no jogo). |
| **Vethgard** | Cidade sugerida para o mapa aberto, próxima da Cratera de Vhalos. |
| **Cratera de Vhalos** | Onde Vashtar encontrou o fragmento de Thanoril. |
| **Sol-3 (Anexo Ínfimo 12)** | Designação da Custódia para a Terra — catálogo baixo, sem relevância aparente. |
| **Enxame Kryvex** | Coletivo alienígena "coletor" (não invasor); sua célula de reconhecimento é a ameaça da primeira missão do jogador (seção 6.5). |
| **Véu de trânsito** | Disfarce passivo dado a operativos da Custódia em mundos de baixa magia/tecnologia — nunca reconstrói o rosto antigo de quem o usa. |

---

## 15. Roteiro de implementação sugerido (fases, não uma corrida)

Ordem sugerida — cada fase é independente e entregável sozinha:

1. **Fase 1 — Reescrever o prólogo.** Trocar `HISTORIA_INICIAL` em `rpg/jogo.py`
   pelo texto expandido (seção 3.1) + o monólogo de Ordinael (seção 3.2),
   adaptando a seleção de raça/classe pra soar como parte da fala.
2. **Fase 2 — Vashtar.** Nova área final de Ilyrath (dungeon ou "trono" único,
   ligado a Habusken), com Vashtar como chefe, e a cutscene de estilhaçamento do
   fragmento (seção 5.2) no final.
3. **Fase 3 — Mapa aberto local.** Um mapa geral de Ilyrath conectando Habusken a
   pelo menos uma cidade nova (Vethgard), com NPCs conversáveis e as primeiras
   Notas/Diários.
4. **Fase 4 — O Vértice e a Custódia.** Hub cósmico, sistema de patentes, e a
   Missão de Sol-3/Retorno à Terra (seção 6.5) como primeira missão de
   Aspirante, seguida das demais missões (Errante/Guardião).
5. **Fase 5 — Arauto/Censor e Nyra Voss.** Missões mais sombrias, gancho da
   investigação, mensagens de Nyra.
6. **Fase 6 — O Relicário.** Os quatro Pilares, Arquivos Absolutos, Théris
   Kalanor.
7. **Fase 7 — Os três finais.** Implementação dos epílogos (com a coda de
   Bianca) e, se fizer sentido mecanicamente, do conteúdo de desafio do Final C.

Nenhuma fase depende de a próxima já existir — dá pra jogar o jogo inteiro parado
em qualquer fase e ele continuar fazendo sentido como uma história completa "por
enquanto".
