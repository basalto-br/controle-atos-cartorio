# Guia de montagem — Controle de Atos no Google Sheets

Versão da ferramenta de controle de protocolos rodando **100% em recursos nativos
do Google Sheets**, sem Google Apps Script.

Arquivo de partida: `Controle-Atos-Cartorio.xlsx` (nesta mesma pasta).

O `.xlsx` traz **estrutura, fórmulas e conteúdo das listas** (a aba `Listas` já vem
preenchida).

O que **não** atravessa a importação, e portanto precisa ser feito à mão (passos 3
a 7): **caixas de seleção**, **validação de dados (listas suspensas)**, **formatação
condicional**, **visualizações de filtro** e **intervalos protegidos**.

Em resumo: do `.xlsx` aproveitam-se os dados e as fórmulas; **todo o comportamento
interativo é montado no Sheets.**

> Isso vale para **importar um `.xlsx`**, que é o que esta seção descreve. Não confunda
> com **copiar uma Planilha Google já pronta** (`Arquivo › Fazer uma cópia`): a cópia
> preserva todos esses quatro itens. Ou seja, você monta **uma vez** a partir do `.xlsx`
> e, daí em diante, move por cópia — nunca por download/re-upload. Ver a seção 10-A.

> **Correção de uma versão anterior deste guia.** O arquivo `.xlsx` contém 13 regras
> de formatação condicional gravadas nele, e este guia afirmava que elas chegariam
> prontas. **Não chegam** — mas o motivo é mais específico do que a primeira correção
> dizia, e a distinção importa:
>
> - **Formatação condicional escrita pelo `openpyxl`** (a deste `.xlsx`) **não é
>   importada.** Testado nas duas rotas — modo de compatibilidade do Office e
>   `Salvar como Planilhas Google` — e o painel aparece vazio nas duas.
> - **Formatação condicional escrita pelo próprio Google Sheets e exportada para
>   `.xlsx` volta normalmente** ao ser reaberta no Sheets. Confirmado em 04/08/2026.
>
> Ou seja: o problema é a origem da regra, não o formato `.xlsx` em si. Para montar
> a partir do arquivo-semente, valem os passos 5 e 5-A.

> **Estado da verificação (05/08/2026).** As fórmulas **foram testadas dentro do Google
> Sheets**, na planilha real do Drive compartilhado — inclusive o cálculo dos 5 dias
> úteis, os blocos dinâmicos do Painel (passo 8-A) e o teste de renomear uma fase
> (passo 8-B). A **lista de feriados** do passo 10 foi conferida em fonte oficial e
> completada para **2026 e 2027**, nas três camadas — nacional, estadual (ES) e
> municipal — e duas datas estavam faltando. Rode o teste de aceitação do passo 9 antes
> de liberar para o setor.
>
> O que continua exigindo atenção não é uma pendência, é uma **rotina**: a lista de
> feriados precisa ganhar o ano seguinte antes de cada dezembro, e o ato anual da CGJES
> sobre o Carnaval precisa ser conferido. Ver o fim do passo 10.
>
> As correções dos passos 8 a 8-C vieram todas de defeito encontrado em uso, não de
> revisão teórica. Cada uma está anotada com o sintoma que a denunciou — é o que
> permite reconhecer o problema de novo se ele voltar por outro caminho.

---

## 1. Importar

1. No Drive **compartilhado do setor** (não no drive pessoal de ninguém):
   `Novo › Upload de arquivo` → `Controle-Atos-Cartorio.xlsx`.
2. Clique com o botão direito no arquivo → `Abrir com › Planilhas Google`.
3. `Arquivo › Salvar como Planilhas Google` (isso gera a versão nativa; o `.xlsx`
   original pode ser mantido como semente).

## 2. Configurar local e fuso — **faça antes de digitar qualquer data**

`Arquivo › Configurações`:

- **Local:** Brasil
- **Fuso horário:** (GMT-03:00) São Paulo
- **Desmarque "Sempre usar os nomes de funções em inglês"**

Sem o local correto, o Sheets interpreta as datas como `mm/dd` e o cálculo dos 5
dias úteis sai errado silenciosamente.

Três coisas observadas na prática, ao converter este arquivo:

1. **O fuso não vem confiável.** Numa conversão veio "(GMT-03:00) São Paulo"; noutra,
   do mesmo arquivo, veio **"(GMT-08:00) Horário do Pacífico"**. Confira sempre, não
   presuma.
2. **A importação liga "Sempre usar os nomes de funções em inglês".** Com essa opção
   ativa, as fórmulas em português dos passos 5 e 8 são rejeitadas ao colar.
3. As fórmulas foram gravadas no `.xlsx` com nomes em inglês (`WORKDAY`,
   `NETWORKDAYS`, `COUNTIFS`) porque é o que o formato exige. Depois de desmarcar a
   opção acima, o Sheets passa a exibi-las como `DIATRABALHO`, `DIATRABALHOTOTAL`,
   `CONT.SES`. Isso é esperado, não é erro.

## 3. Caixas de seleção

Selecione cada intervalo e use `Inserir › Caixa de seleção`:

| Aba | Intervalo | Coluna |
|---|---|---|
| Protocolos | `M2:M1000` | Doc. completa? |
| Protocolos | `S2:S1000` | Digitalizado? |
| Protocolos | `Y2:Y1000` | Arquivado? |
| Checklist | `C2:C1001` | Entregue? |

As células já vêm com `FALSO`, então viram caixas desmarcadas.

> **Por que 1000 e não 301.** O `.xlsx` só traz dados e fórmulas até a linha 301, mas
> não há razão para a *entrada de dados* parar ali. Depois do passo 8 as fórmulas
> passam a cobrir a coluna inteira, então o teto real vira o alcance das caixas de
> seleção e das listas suspensas. Deixe tudo em 1000 desde o começo — é bem mais
> chato descobrir isso depois, com a planilha em uso.

> **O Sheets pode dividir a regra em duas.** Se você aplicar a caixa de seleção em
> `M2:M301` e mais tarde alargar para `M2:M1000`, o painel de validação passa a mostrar
> **duas** regras de caixa de seleção (`M2:M301` e `M302:M1000`) em vez de uma. É
> normalização do próprio Sheets, não erro: a cobertura fica completa e o comportamento
> é idêntico. Não tente "consertar" apagando uma delas.

## 4. Criar as listas suspensas — **também não vêm no `.xlsx`**

O arquivo contém as validações, mas o Sheets **não as importa** — mesma falha da
formatação condicional (regra escrita pelo `openpyxl` é descartada). O sintoma é
direto: ao cadastrar um protocolo, nada é oferecido em lista e tudo tem de ser
digitado à mão.

Para cada linha da tabela: **selecione o intervalo de aplicação primeiro** (caixa de
nome, canto superior esquerdo), depois `Dados › Validação de dados › Adicionar regra`,
escolha **"Menu suspenso (de um intervalo)"** e cole a origem.

| Coluna | Intervalo de aplicação | Origem |
|---|---|---|
| E — PF/PJ | `E2:E1000` | `Listas!$M$2:$M$5` |
| I — Tipo de ato | `I2:I1000` | `Listas!$A$2:$A$100` |
| K — Canal | `K2:K1000` | `Listas!$K$2:$K$20` |
| L — Responsável | `L2:L1000` | `Listas!$I$2:$I$50` |
| R — Fase | `R2:R1000` | `Listas!$D$2:$D$100` |
| W — Atualizado por | `W2:W1000` | `Listas!$I$2:$I$50` |
| Checklist A — ID Protocolo | `A2:A1001` | `Protocolos!$A$2:$A$1000` |

> **Mantenha o intervalo de origem mais largo que a lista de hoje.** `Listas!$D$2:$D$100`
> para 8 fases parece exagero, mas é isso que permite acrescentar uma fase nova sem
> reeditar a regra. O mesmo vale para `$I$2:$I$50` nos responsáveis. E confira que o
> Painel (passo 8-A) lê **o mesmo intervalo** — se a lista suspensa lê até a linha 100
> e o Painel só até a 40, uma fase cadastrada na linha 41 fica selecionável no protocolo
> e invisível no Painel.

A última (ID do protocolo na aba Checklist) é o que evita lançar documento para um
protocolo que não existe.

> ⚠️ **Não edite o campo "Aplicar ao intervalo" para criar a regra seguinte.** Depois de
> clicar em `Adicionar regra`, o campo vem preenchido com o intervalo selecionado; se você
> trocar o texto ali para outro intervalo, o Sheets **move a regra anterior** em vez de
> criar uma nova — e você fica com uma regra só, na coluna errada. Selecione o intervalo
> na planilha **antes** de abrir `Adicionar regra`, e não toque nesse campo.

Ao terminar, confira abrindo `Dados › Validação de dados` com a planilha inteira
selecionada. **Não conte as regras — confira as colunas.** O Sheets reorganiza a lista
por conta própria: junta `L` e `W` numa regra só (têm a mesma origem) e pode partir a de
caixa de seleção em duas por faixa de linhas. O que importa é que toda coluna da tabela
acima apareça coberta, do intervalo `2` até o `1000`.

> **Editar "Aplicar ao intervalo" numa regra que já existe é seguro** — é justamente
> como se alarga o intervalo depois. O que não pode é editar esse campo **para criar a
> regra seguinte**, como diz o aviso acima. São duas operações diferentes no mesmo campo.

## 5. Formatação condicional — **montar à mão, uma a uma**

Selecione o intervalo, abra `Formatar › Formatação condicional › Adicionar outra
regra`, escolha **"A fórmula personalizada é"** (é a última opção do menu suspenso,
precisa rolar) e cole a fórmula. As fórmulas abaixo já estão em pt-BR com `;`.

**Bloco principal — selecione `A2:Z1000` antes de começar.** Crie nesta ordem, porque
a primeira regra que casar define o fundo da célula:

| # | Fórmula | Formato |
|---|---|---|
| 1 | `=$Y2=VERDADEIRO` | fundo cinza claro, texto cinza (arquivado) |
| 2 | `=E(SEERRO(PROCV($R2;INDIRETO("Listas!$D$2:$F$100");3;FALSO);"Nao")="Sim";$S2=FALSO)` | fundo vermelho forte, texto branco |
| 3 | `=$Q2="Atrasado"` | fundo vermelho claro, texto vermelho escuro |
| 4 | `=$Q2="Vence hoje"` | fundo âmbar, texto laranja escuro |
| 5 | `=$Q2="Concluído"` | fundo verde claro, texto verde escuro |
| 6 | `=E($M2=VERDADEIRO;$U2<>"";$U2<1)` | sem fundo, texto âmbar em negrito |

> **Duas armadilhas na regra 2, e as duas custam tempo.**
>
> 1. **Formatação condicional não aceita referência direta a outra aba.** Escrever
>    `Listas!$D$2:$F$100` faz o Sheets recusar com "Fórmula inválida". É obrigatório
>    envolver em `INDIRETO("…")`. Isso vale para qualquer regra que precise consultar
>    a `Listas`.
> 2. **A regra não pergunta se a fase se chama "Finalizado"** — pergunta se a fase
>    **exige digitalização**, lendo a coluna F da `Listas`. Era `=E($R2="Finalizado";$S2=FALSO)`
>    e isso quebrava em silêncio no dia em que alguém renomeasse a fase em Configurações.
>    Ver o passo 8-B.

**Regras em intervalos próprios:**

| Intervalo | Fórmula | Formato |
|---|---|---|
| `Protocolos!A2:A1000` | `=E($A2<>"";CONT.SE($A$2:$A$1000;$A2)>1)` | vermelho claro, negrito (ID duplicado) |
| `Protocolos!B2:B1000` | `=E($B2<>"";CONT.SE($B$2:$B$1000;$B2)>1)` | vermelho claro, negrito (Nº DRD duplicado) |
| `Checklist!A2:D1001` | `=$C2=VERDADEIRO` | texto cinza (documento já entregue) |

**Cor por escrevente.** Em `Protocolos!L2:L1000`, uma regra por nome
(`=$L2="Escrevente 1"`, `=$L2="Escrevente 2"`, `=$L2="Escrevente 3"`), cada uma com um
fundo claro diferente. Serve para bater o olho na visão geral. Troque pelos nomes
reais conforme a **seção 12**.

Como as regras do bloco principal vêm antes e têm "Parar se for verdadeiro", a cor do
escrevente **não aparece** em linha atrasada, arquivada ou concluída — nessas, o
estado do protocolo vence. É o comportamento desejado.

> Não é possível, sem Apps Script, esmaecer automaticamente "as linhas que não são
> minhas": nenhuma fórmula nativa sabe quem está com a planilha aberta. A cor por
> escrevente é o substituto mais próximo; a separação de verdade é a visualização de
> filtro do passo 6.

**A regra de "ID inexistente" na aba Checklist não é necessária** — a validação de
dados do passo 4 (menu suspenso vindo de `Protocolos!$A$2:$A$1000`) já sinaliza um ID
que não existe, com o mesmo efeito e sem uma regra extra.

## 6. Visualizações de Filtro — a peça central do uso simultâneo

**Selecione `A1:Z1000` antes de criar cada visualização.** A visualização nasce com o
intervalo que estiver selecionado; se você criar com uma única coluna selecionada,
ela filtra só aquela coluna e não esconde as linhas da tabela.

Depois: `Dados › Criar visualização com filtro`, clique no ícone de filtro no
cabeçalho da coluna, escolha **"Filtrar por condição"**, defina o critério, `OK`, e
`Salvar visualização` no topo, dando o nome.

| Nome | Coluna | Condição |
|---|---|---|
| `Minhas — Escrevente 1` | L Responsável | O texto é exatamente `Escrevente 1` |
| `Minhas — Escrevente 2` | L Responsável | O texto é exatamente `Escrevente 2` |
| `Minhas — Escrevente 3` | L Responsável | O texto é exatamente `Escrevente 3` |
| `Vencem hoje` | Q Situação | O texto é exatamente `Vence hoje` |
| `Atrasados` | Q Situação | O texto é exatamente `Atrasado` |
| `Aguardando assinatura` | R Fase | O texto é exatamente `Aguardando assinatura` |
| `Arquivados` | Y Arquivado? | A fórmula personalizada é `=$Y2=VERDADEIRO` |

`Arquivados` usa fórmula, e não filtro por valores, porque enquanto nenhum protocolo
tiver sido arquivado a lista de valores da coluna só oferece `FALSE` — não há
`VERDADEIRO` para marcar.

Ao salvar, o Sheets avisa que "visualizações que se sobrepõem a um intervalo
protegido não serão salvas". Na prática as sete foram salvas normalmente mesmo com
as proteções do passo 7 já aplicadas; o aviso é preventivo.

> **Use "Filtrar por condição", não "Filtrar por valores"**, nas seis primeiras. O
> filtro por valores guarda a lista de valores *escondidos* e só conhece os que já
> existem na coluna hoje — quando um nome novo aparecer, ele passa a vazar para
> dentro da visualização de outra pessoa. A condição de texto continua correta para
> qualquer linha futura.

**Regra de convívio, e ela não é opcional:** nunca usar o filtro comum
(`Dados › Criar um filtro`). O filtro comum muda a tela de **todos** que estiverem
com a planilha aberta; a visualização de filtro é individual. Vale combinar isso
com as três escreventes no primeiro dia.

O mesmo vale para **Segmentações de dados**: elas também são estado compartilhado.
Se usar, use só na aba `Painel`, ciente de que mexer nelas muda o que os outros veem.

## 7. Intervalos protegidos

`Dados › Proteger planilhas e intervalos`:

| Alvo | Ação |
|---|---|
| Aba `Listas` inteira (guia **Página**) | restringir a quem administra a planilha |
| Aba `Painel` inteira (guia **Página**) | restringir (é só leitura) |
| `Protocolos!J1:J1000` | restringir — Categoria (calculada) |
| `Protocolos!O1:Q1000` | restringir — Prazo, Dias úteis restantes, Situação |
| `Protocolos!U1:U1000` | restringir — % Checklist |
| Linha 1 de todas as abas | restringir |
| Resto de `Protocolos` e `Checklist` | `Mostrar um aviso ao editar` (avisa sem bloquear) |

`O1:Q1000` cobre as três colunas calculadas contíguas de uma vez — não precisa de uma
proteção por coluna.

> **A proteção começa na linha 1, não na 2.** Depois do passo 8 a fórmula-mestre de
> cada coluna calculada mora na **linha 1** (é ela que gera o próprio cabeçalho). Se a
> proteção começar na linha 2, o cabeçalho fica desprotegido e uma edição acidental ali
> apaga a coluna inteira.

> **O menu Dados muda de tamanho.** Na aba onde existem visualizações de filtro
> salvas, aparecem dois itens a mais ("Mudar visualização", "Opções de visualização")
> e tudo abaixo desce. Confira o rótulo antes de clicar: logo acima de
> `Proteger páginas e intervalos` fica `Adicionar um controle de filtros`, que insere
> uma segmentação de dados na planilha.

## 8. Melhoria recomendada — trocar as fórmulas repetidas por `ARRAYFORMULA`

No `.xlsx` as colunas calculadas estão **repetidas linha a linha até a 301**,
porque é o formato que a importação carrega sem risco. Isso tem dois defeitos:
a linha 302 em diante não calcula, e um escrevente pode apagar a fórmula sem notar.

Já dentro do Sheets, vale substituir por uma fórmula única por coluna. Para cada
coluna abaixo: **apague o intervalo inteiro, incluindo o cabeçalho** (ex. `J1:J301`)
e cole a fórmula **apenas na linha 1** (`J1`).

> **Por que na linha 1 e não na 2.** Se a fórmula-mestre mora na linha 2, ela é a
> primeira coisa que morre quando alguém apaga a linha de teste — foi exatamente o que
> aconteceu aqui, e a coluna Categoria ficou em branco sem ninguém entender por quê.
> Colocando na linha 1 e fazendo a própria fórmula gerar o cabeçalho
> (`SE(LIN($A$1:$A)=1;"Categoria";…)`), a linha 1 nunca é apagada no uso normal e
> **qualquer linha de dados vira descartável**. As proteções do passo 7 já começam na
> linha 1 por causa disso.

**J1 — Categoria**
```
=ARRAYFORMULA(SE(LIN($A$1:$A)=1;"Categoria";SE($I$1:$I="";"";SEERRO(PROCV($I$1:$I;Listas!$A$2:$B$100;2;FALSO);"—"))))
```

**O1 — Prazo**
```
=ARRAYFORMULA(SE(LIN($A$1:$A)=1;"Prazo";SEERRO(SE($N$1:$N="";"";DIATRABALHO($N$1:$N;5;Listas!$O$2:$O$200));"")))
```

**P1 — Dias úteis restantes**
```
=ARRAYFORMULA(SE(LIN($A$1:$A)=1;"Dias úteis restantes";SEERRO(SE($O$1:$O="";"";SE($O$1:$O>=HOJE();DIATRABALHOTOTAL(HOJE();$O$1:$O;Listas!$O$2:$O$200)-1;DIATRABALHOTOTAL(HOJE();$O$1:$O;Listas!$O$2:$O$200)+1));"")))
```

**Q1 — Situação** (ver o passo 8-B: não cita nome de fase)
```
=ARRAYFORMULA(SE(LIN($A$1:$A)=1;"Situação";SEERRO(SE($O$1:$O="";"";SE(SEERRO(PROCV($R$1:$R;Listas!$D$2:$E$100;2;FALSO);"Nao")="Sim";SE(SEERRO(PROCV($R$1:$R;Listas!$D$2:$F$100;3;FALSO);"Nao")="Sim";"Concluído";"Encerrado");SE($P$1:$P<0;"Atrasado";SE($P$1:$P=0;"Vence hoje";"No prazo"))));"")))
```

**U1 — % Checklist**
```
=ARRAYFORMULA(SE(LIN($A$1:$A)=1;"% Checklist";SEERRO(SE($A$1:$A="";"";CONT.SES(Checklist!$A$2:$A$3000;$A$1:$A;Checklist!$C$2:$C$3000;VERDADEIRO)/CONT.SE(Checklist!$A$2:$A$3000;$A$1:$A));"")))
```

Depois de colar, confira que a linha 1 continua exibindo o texto do cabeçalho — se
aparecer `0` ou vazio, a parte `LIN(...)=1` não pegou.

## 8-A. Painel — blocos que acompanham a `Listas` sozinhos

Os blocos "Por fase" e "Por escrevente" nasceram com os rótulos **digitados à mão**.
O efeito prático: cadastrar uma fase nova em Configurações não fazia nada aparecer no
Painel, e ninguém lembrava de ir lá copiar fórmula e inserir linha.

A correção é dar a cada bloco um número fixo de **vagas**, preenchidas por fórmula a
partir da `Listas`.

**Antes de mexer nas fórmulas, reserve espaço.** Selecione as 4 linhas onde começa
"Por escrevente" e faça `Inserir › 4 linhas acima`. Sem essa folga os dois blocos
colidem quando a lista de fases crescer. Layout final:

| Linhas | Conteúdo |
|---|---|
| 13 | título "Por fase (não arquivados)" + avisos em `D13` e `D14` |
| 14–25 | 12 vagas de fase |
| 26–27 | respiro |
| 28 | título "Por escrevente" + aviso em `F28` |
| 29 | cabeçalho (Em andamento / Atrasados / Vencem hoje) |
| 30–49 | 20 vagas de escrevente |

**`B14` — rótulos das fases** (cole em `B14` e arraste até `B25`)
```
=SEERRO(ÍNDICE(FILTER(Listas!$D$2:$D$100;Listas!$D$2:$D$100<>"");LIN()-13);"")
```

**`C14` — contagem** (cole em `C14` e arraste até `C25`)
```
=SE($B14="";"";SOMARPRODUTO((Protocolos!$R$2:$R$1000=$B14)*(Protocolos!$Y$2:$Y$1000=FALSO)))
```

**`B30` — nomes dos escreventes** (cole em `B30` e arraste até `B49`)
```
=SEERRO(ÍNDICE(FILTER(Listas!$I$2:$I$50;Listas!$I$2:$I$50<>"");LIN()-29);"")
```

**`C30` / `D30` / `E30` — as três contagens** (cole e arraste cada uma até a linha 49)
```
=SE($B30="";"";SOMARPRODUTO((Protocolos!$A$2:$A$1000<>"")*(Protocolos!$L$2:$L$1000=$B30)*(Protocolos!$Y$2:$Y$1000=FALSO)*(SEERRO(PROCV(Protocolos!$R$2:$R$1000;Listas!$D$2:$E$100;2;FALSO);"Nao")<>"Sim")))
```
```
=SE($B30="";"";SOMARPRODUTO((Protocolos!$L$2:$L$1000=$B30)*(Protocolos!$Q$2:$Q$1000="Atrasado")))
```
```
=SE($B30="";"";SOMARPRODUTO((Protocolos!$L$2:$L$1000=$B30)*(Protocolos!$Q$2:$Q$1000="Vence hoje")))
```

**Dois avisos que só aparecem quando há problema.** Ficam em branco no dia a dia:

`D13` — estourou a capacidade de vagas
```
=SE(CONT.VALORES(Listas!$D$2:$D$100)>12;"(!) Mais de 12 fases cadastradas - o Painel mostra so as 12 primeiras. Insira linhas antes do bloco 'Por escrevente' e arraste B/C para baixo.";"")
```

`D14` — protocolo com fase que não existe mais na lista (típico de renomeação)
```
=SE(CONT.SES(Protocolos!$R$2:$R$1000;"<>";Protocolos!$Y$2:$Y$1000;FALSO)-SOMA($C$14:$C$25)=0;"";"(!) "&(CONT.SES(Protocolos!$R$2:$R$1000;"<>";Protocolos!$Y$2:$Y$1000;FALSO)-SOMA($C$14:$C$25))&" protocolo(s) com fase fora da lista - nao aparecem acima.")
```

`F28` — estourou a capacidade de escreventes
```
=SE(CONT.VALORES(Listas!$I$2:$I$50)>20;"(!) Mais de 20 escreventes cadastrados - o Painel mostra so os 20 primeiros. Arraste B30:E49 para baixo.";"")
```

> **Vagas fixas, não fórmula que se expande.** É tentador usar `FILTER` sozinho e deixar
> o resultado "derramar" pelas linhas abaixo. **Não faça isso aqui.** Quando o resultado
> não couber no espaço livre, o Sheets não corta o excesso — ele **recusa a expansão
> inteira** e a célula vira `#REF!` ("a matriz não foi expandida porque substituiria os
> dados em B28"). O bloco todo some de uma vez, e `SEERRO` **não** captura esse erro,
> porque é erro de expansão e não de valor. Com vagas fixas o pior caso é uma fase a
> mais não aparecer — e o aviso de `D13` diz exatamente isso.

## 8-B. Nunca cite o nome de uma fase dentro de uma fórmula

Este é o princípio mais importante da manutenção da planilha, e custou uma rodada
inteira de correção para aparecer.

Várias fórmulas nasceram perguntando `$R2="Finalizado"` ou `$R2="Usuário desistiu"`.
Como o usuário **pode renomear qualquer fase** em Configurações, essas fórmulas quebram
em silêncio — sem erro, sem célula vermelha, só número errado. Testado renomeando
"Finalizado" para "Encerrado": a contagem de "Em andamento" passou a incluir o ato
concluído, e o alerta "Finalizado sem digitalização" foi para zero.

A `Listas` já tem as duas colunas que respondem isso de verdade:

| Coluna | Pergunta que responde |
|---|---|
| `E` — É final? | a fase encerra o protocolo? |
| `F` — Exige digitalização? | a fase exige rascunho digitalizado? |

**Consulte a coluna, nunca o nome.** Os quatro lugares corrigidos:

| Onde | O que passou a perguntar |
|---|---|
| `Protocolos!Q` — Situação (passo 8) | é final? e exige digitalização? |
| `Painel!C9` — Finalizado sem digitalização | exige digitalização? |
| `Painel!C30:C49` — Em andamento (passo 8-A) | é final? |
| Formatação condicional, regra 2 (passo 5) | exige digitalização? |

**`Painel!C9` — Finalizado sem digitalização**
```
=SOMARPRODUTO((SEERRO(PROCV(Protocolos!$R$2:$R$1000;Listas!$D$2:$F$100;3;FALSO);"Nao")="Sim")*(Protocolos!$S$2:$S$1000=FALSO))
```

> **Os dois rótulos da Situação continuam existindo.** "Concluído" e "Encerrado" foram
> preservados sem citar nome nenhum: final **e** exige digitalização → "Concluído";
> final **e** não exige → "Encerrado". Bate exatamente com o comportamento antigo,
> porque é assim que as duas fases finais estão configuradas na `Listas`.

## 8-C. Armadilhas de fórmula neste ambiente

Quatro coisas que custaram tempo e não estão em lugar nenhum óbvio:

**1. `FILTRO` não existe. A função é `FILTER`.** O Sheets em português traduz
`ÍNDICE`, `SOMARPRODUTO`, `CONT.SES`, `PROCV`, `SEERRO` — mas **não** traduz `FILTER`.
Escrever `FILTRO` devolve `#NAME? — Função desconhecida`.

**2. `SEERRO` esconde o erro do item 1.** Uma fórmula com `FILTRO` dentro de um
`SEERRO` não mostra erro nenhum: devolve vazio, e a contagem ao lado passa a contar
linhas em branco. Parece que funciona. **Para diagnosticar, tire o `SEERRO` e rode a
fórmula crua numa célula livre** — só assim o `#NAME?` aparece.

**3. `CONT.SES` trata `*` e `?` como curinga; `SOMARPRODUTO` compara exato.** Por isso
as contagens do Painel usam `SOMARPRODUTO`. Se alguém renomear uma fase para algo com
"?" no fim, uma versão em `CONT.SES` passaria a contar demais, em silêncio.

**4. Formatação condicional não enxerga outra aba.** Qualquer regra que precise ler a
`Listas` tem de envolver a referência em `INDIRETO("Listas!$D$2:$F$100")`, senão o
Sheets recusa com "Fórmula inválida".

## 9. Teste de aceitação — antes de liberar para o setor

Crie um protocolo de teste e confira, um a um:

1. **Prazo.** Data doc. completa = uma segunda-feira → `Prazo` deve cair na
   segunda-feira seguinte (5 dias úteis).
2. **Prazo com feriado.** Ponha uma data cujo intervalo inclua um feriado da aba
   `Listas` → o prazo deve andar um dia a mais.
3. **Vence hoje.** Ajuste a data doc. completa para o prazo cair hoje →
   `Dias úteis restantes` = 0 e `Situação` = "Vence hoje".
4. **Atrasado.** Prazo no passado → `Situação` = "Atrasado", linha em vermelho claro.
5. **Fase final.** Mude a fase para "Finalizado" → `Situação` vira "Concluído" e a
   linha fica vermelho forte enquanto `Digitalizado?` estiver desmarcado.
6. **Checklist.** Lance 4 documentos na aba `Checklist` com o ID do teste, marque 2 →
   `% Checklist` = 50%.
7. **ID duplicado.** Repita o ID em outra linha → as duas células ficam vermelhas.
8. **Painel.** Confira se os contadores refletem o protocolo de teste.
9. **Fase nova aparece sozinha.** Acrescente uma fase em `Listas!D` → ela deve surgir
   no bloco "Por fase" do Painel, com contagem, **sem** você mexer no Painel. Apague
   depois — a linha deve sumir limpa, sem erro e sem sobra.
10. **Escrevente novo aparece sozinho.** Mesma coisa em `Listas!I` para o bloco
    "Por escrevente".
11. **Renomear uma fase não quebra nada** — este é o teste que mais pega defeito.
    Renomeie "Finalizado" em `Listas!D` para outra coisa, e ponha um protocolo nessa
    fase. Devem continuar certos, todos os quatro: `Situação` = "Concluído", a linha
    em vermelho forte, o alerta "Finalizado sem digitalização" contando, e o protocolo
    **fora** de "Em andamento" no bloco por escrevente. Desfaça a renomeação depois.
12. **Linha muito abaixo.** Lance um protocolo na linha 500 → listas suspensas e caixas
    de seleção devem estar lá, e o Painel deve contá-lo. É o que prova que o teto de
    1000 linhas valeu para tudo, e não só para as fórmulas.
13. **Simultâneo.** Abra com duas contas ao mesmo tempo, cada uma na sua
    visualização de filtro, e edite linhas diferentes — nenhuma deve interferir na outra.

Depois apague as linhas de teste (e as linhas de checklist delas).

> **Apagar a linha de teste ficou seguro.** Depois do passo 8 a fórmula-mestre mora na
> linha 1, então limpar qualquer linha de dados não derruba mais nenhuma coluna
> calculada. Antes disso derrubava — e sem aviso.

> O item 3 tem uma borda conhecida: se você abrir a planilha num **sábado ou
> domingo**, a contagem de dias úteis pode marcar como "vence hoje" o prazo que na
> verdade é da segunda-feira. Como o setor trabalha em dia útil, isso foi aceito
> em vez de complicar a fórmula.

## 10. Feriados — a lista de que todo o prazo depende

A aba `Listas` traz as datas na coluna **O** e a descrição com o fundamento legal na
coluna **P**. As fórmulas de prazo leem `Listas!$O$2:$O$200`, então há folga de sobra
para acrescentar anos.

**Todo o cálculo dos 5 dias úteis depende dessa lista** — uma data faltando encurta o
prazo em silêncio, sem erro e sem aviso. É o item que mais merece cuidado.

### Três camadas, e a terceira é a que costuma faltar

| Camada | Fonte | Exemplo |
|---|---|---|
| Nacional | Lei 662/1949 (red. Lei 10.607/2002), Lei 6.802/1980, Lei 14.759/2023 | Tiradentes, Natal, Consciência Negra |
| Estadual (ES) | Lei Estadual 11.010/2019 | Nossa Senhora da Penha — segunda-feira, 8º dia após a Páscoa |
| **Municipal** | Lei de feriados **do município da serventia** | Sexta-feira da Paixão, Corpus Christi, o padroeiro do município |

A camada municipal é a mais fácil de esquecer e a que mais varia. A **Lei federal
9.093/1995** permite até **quatro** feriados religiosos municipais, já incluída aí a
Sexta-feira da Paixão — e é comum que o município use os quatro. **Essa parte da lista
não dá para copiar de ninguém:** procure a lei de feriados do próprio município, e
refaça tudo se a serventia mudar de cidade.

> **Duas datas estavam faltando, e só a conferência real as revelou (05/08/2026):**
>
> - **Nossa Senhora da Penha** — feriado estadual de todo o ES, não estava na lista.
> - **O feriado do padroeiro do município** — também não estava. E ele cai **colado
>   num feriado nacional**, formando um bloco de dois dias seguidos. Um protocolo cujo
>   prazo atravessava esse bloco vencia **dois dias antes** do que devia.
>
> A lição não é a data em si: é que **feriado municipal esquecido não dá erro nenhum**.
> A planilha continua calculando, com toda a cara de certa, e entrega um prazo curto.

### Ponto facultativo não é feriado para cartório

O **Código de Normas CGJES — Foro Extrajudicial, art. 13, §2º** diz que feriado forense
e ponto facultativo **não interferem** no funcionamento de notas e registros, salvo ato
que expressamente alcance o extrajudicial. O **Ato Normativo TJES nº 319/2025, art. 5º**
reforça: seus efeitos não se aplicam às serventias extrajudiciais.

Consequência prática: **Carnaval não é feriado**. Em 2026 a serventia fechou porque
houve ato específico — **Ofício Circular CGJES nº 3050010/2026**, que autorizou não
funcionar em 16 e 17/02 e abrir a partir das 12h na Quarta-feira de Cinzas. Por isso a
Quarta-feira de Cinzas **não** entra na lista (há expediente), e o Carnaval entra
marcado como dependente de ato anual.

Já **Corpus Christi e Sexta-feira da Paixão costumam ser feriado municipal de lei** —
e aí entram sem depender de ato nenhum da Corregedoria. Confira na lei do município: é
a diferença entre fechar por direito e fechar por autorização que precisa ser renovada
todo ano.

### Manutenção anual — não é opcional

1. **Antes de dezembro, acrescente o ano seguinte.** Um protocolo lançado no fim de
   dezembro tem prazo que cruza o ano; sem as datas do ano novo, 01/01 é contado como
   dia útil. A lista hoje cobre **2026 e 2027**.
2. **Recalcule as móveis pela Páscoa.** Sexta-feira da Paixão = Páscoa − 2 dias;
   Carnaval = 48 e 47 dias antes; Corpus Christi = 60 dias depois; N. Sra. da Penha =
   segunda-feira, 8º dia depois. Páscoa: **05/04/2026**, **28/03/2027**.
3. **Confira o ato da CGJES sobre Carnaval** de cada ano — é ele que autoriza fechar.

Depois de mexer na lista, refaça o item 2 do teste de aceitação (passo 9) com uma data
que atravesse o feriado novo. É o único jeito de ver que ela pegou.

## 10-A. Levar a planilha pronta para o Workspace do cartório

Não é preciso remontar nada. `Arquivo › Fazer uma cópia` carrega fórmulas, formatação
condicional, validação de dados, caixas de seleção, intervalos nomeados, intervalos
protegidos, **visualizações de filtro** e as configurações de local e fuso — tudo
confirmado numa migração real, ver a verificação no fim desta seção.

> ⛔ **Nunca mova a planilha pronta baixando-a como `.xlsx` e subindo de novo.** É o
> caminho que parece óbvio e é o que destrói o trabalho: **caixas de seleção,
> visualizações de filtro e intervalos protegidos não existem no formato `.xlsx`** e
> somem na volta. Aconteceu de fato em 04/08/2026 — o arquivo chegou ao Drive
> compartilhado com a formatação condicional intacta e com a coluna "Doc. completa?"
> exibindo `FALSE` como texto, sem nenhuma caixa de seleção, sem visualização de filtro
> e sem proteção. **Só `Fazer uma cópia` preserva tudo.**

**Ordem recomendada:**

1. Apague a linha de teste (e as linhas de checklist dela).
2. Compartilhe o arquivo com a sua conta do Workspace.
3. **Logado na conta do Workspace**, abra o arquivo e faça
   `Arquivo › Fazer uma cópia`, escolhendo como destino o **Drive compartilhado do
   setor**. A cópia nasce com a organização como proprietária — isso evita a
   transferência de propriedade entre conta pessoal e domínio corporativo, que é o
   passo que costuma ser bloqueado por política.

**O que precisa ser refeito ou conferido do outro lado:**

| Item | Por quê |
|---|---|
| Lista de "quem pode editar" das 5 proteções | A proteção é copiada, mas as permissões são reancoradas em quem fez a cópia. Refaça apontando para as contas reais das escreventes |
| Caixas de seleção de linhas já limpas | Se você apagou a linha de teste antes de copiar, as caixas daquela linha somem junto. Reaplique `Inserir › Caixa de seleção` sobre `M2:M1000`, `S2:S1000` e `Y2:Y1000` — reaplicar sobre células que já são caixas é inofensivo |
| Feriados | Continuam pendentes de verificação, independentemente da cópia |

**Verificado na cópia real (04/08/2026)**, item a item: formato Planilha Google nativa;
propriedade da organização (sem dono individual, como é próprio de Drive compartilhado);
**local Brasil e fuso São Paulo vieram corretos**; formatação condicional completa;
intervalos protegidos com cadeado nas abas; e **as 7 visualizações de filtro atravessaram**.
Nenhum compartilhamento foi herdado, porque a caixa "Compartilhar com as mesmas pessoas"
ficou desmarcada no diálogo de cópia — **deixe-a desmarcada**, ou a cópia arrasta consigo
quem tinha acesso na origem.

> **O seletor de pasta é a prova da conta.** Ao escolher o destino, o Drive compartilhado
> só aparece na lista se a sessão do navegador estiver na conta do Workspace. Se ele não
> aparecer, você está logado na conta errada — pare e troque, em vez de salvar em
> "Meu Drive".

> **Proteção de intervalo não é controle de segurança.** Em Drive compartilhado, quem
> tiver papel de **Gerente** ou **Gerente de conteúdo** consegue alterar ou remover
> proteções. Para que as proteções realmente segurem, as três escreventes devem
> entrar como **Colaborador**, e o papel de Gerente ficar com quem administra a
> planilha. Proteção serve contra erro de digitação, não contra quem quer mudar.

## 11. Compartilhamento e proteção de dados

A ferramenta anterior guardava tudo no computador do usuário. Esta guarda no
Workspace, então algumas decisões passam a ser explícitas:

- Manter em **Drive compartilhado do setor**, nunca no drive pessoal de um escrevente
  (se a pessoa sai, o arquivo vai junto).
- **Desligar o compartilhamento externo** e o acesso por link.
- Dar `Editor` só às três escreventes; tabelião e demais interessados como `Leitor`.
- O **Histórico de versões guarda o que foi apagado**. "Excluir" uma linha não é
  expurgo de dado — por isso a coluna `Arquivado?` existe: arquivar é o caminho
  normal, apagar é exceção.
- Fazer periodicamente `Arquivo › Fazer uma cópia` como backup frio; o histórico de
  versões é bom contra erro de digitação, não contra exclusão do arquivo inteiro.

## 12. Trocar `Escrevente 1/2/3` pelos nomes reais

Este material fica em repositório **público**, então a planilha-semente vem com nomes
genéricos. Os nomes reais das escreventes nunca devem ser commitados aqui — eles vivem
só na planilha do Drive, que é privada.

Depois de importar, faça a troca **nesta ordem**. A ordem importa: se você renomear na
`Listas` por último, as validações passam a apontar para nomes que não existem mais e
as células já preenchidas ficam marcadas como inválidas.

1. **`Listas`, coluna I** — substitua `Escrevente 1/2/3` pelos nomes reais.
   A aba está protegida; desproteja, edite e proteja de novo.
2. **`Protocolos`, colunas L e W** — se já houver protocolos lançados, use
   `Editar › Localizar e substituir` (`Ctrl+H`) marcando **"Pesquisar em todas as
   páginas"**, um nome por vez. As listas suspensas se atualizam sozinhas, porque
   apontam para a `Listas`.
3. **Formatação condicional** — em `Protocolos!L2:L1000`, edite as 3 regras de cor por
   escrevente (passo 5) trocando o nome dentro de cada fórmula.
4. **Visualizações de filtro** — em cada uma das 3 `Minhas — …` (passo 6), renomeie a
   visualização e ajuste a condição de texto. Renomear a visualização **não** muda o
   critério; são duas edições separadas.

**O `Painel` não entra mais nesta lista.** Depois do passo 8-A ele lê os nomes direto
da `Listas` — trocar em `Listas!I` já muda o Painel sozinho.

**Para acrescentar uma quarta escrevente**, só duas coisas: adicione o nome em
`Listas!I5` e crie a visualização de filtro `Minhas — <nome>`. Painel e validações de
dados se viram sozinhos. Se quiser a cor por escrevente também para ela, acrescente uma
quarta regra de formatação condicional (passo 5) — essa continua sendo manual, porque
formatação condicional não sabe gerar uma regra por item de lista.

**Se preferir regenerar do zero**, edite `RESPONSAVEIS` em `gerar_planilha.py` e rode
o script; mas aí você perde tudo que foi montado à mão (passos 3 a 7). Só compensa
antes da primeira importação.

## 13. Limitações conhecidas desta versão

Consequências diretas de não usar Apps Script — não são defeitos a corrigir, são o
preço da restrição:

| Limitação | Contorno adotado |
|---|---|
| Nenhum carimbo automático de data/hora | Colunas `Última atualização` + `Atualizado por`, preenchidas à mão (`Ctrl+;` insere a data de hoje) |
| Sem histórico de mudança de fase | **Comentário nativo** na linha (`Ctrl+Alt+M`) — grava autor e data/hora sozinho. É o único registro automático que sobra |
| Nenhuma regra pode ser bloqueante | Todas viram alerta visual (vermelho/âmbar). A planilha avisa, não impede |
| Numeração de protocolo não é automática | `Painel!C2` sugere o próximo ID; a formatação condicional acusa duplicado |
| Linhas de checklist não são geradas sozinhas | Blocos-modelo na aba `Listas` (colunas R e S) para copiar e colar |
| Não há trava de linha por usuário | Visualizações de filtro + coluna `Responsável`. Duas pessoas só conflitam se editarem **a mesma célula** no mesmo instante |
| Sem lixeira de verdade | Coluna `Arquivado?` + visualização `Arquivados` |

## 14. Fora do escopo desta primeira versão

Ficaram para uma segunda rodada, depois que o núcleo for validado no uso real:
**Tarefas**, **atos de balcão**, **vínculo entre protocolos**, **pendências** e
**relatório do dia**. Todos são portáveis com o mesmo desenho (aba própria + ID do
protocolo como chave).
