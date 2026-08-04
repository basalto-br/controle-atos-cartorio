# Guia de montagem — Controle de Atos no Google Sheets

Versão da ferramenta de controle de protocolos rodando **100% em recursos nativos
do Google Sheets**, sem Google Apps Script.

Arquivo de partida: `Controle-Atos-Cartorio.xlsx` (nesta mesma pasta).

O `.xlsx` traz **estrutura, fórmulas, listas suspensas e validação de dados**.

O que **não** atravessa a importação, e portanto precisa ser feito à mão (passos 3
a 7): **caixas de seleção**, **formatação condicional**, **visualizações de filtro**
e **intervalos protegidos**.

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

> **Aviso de verificação.** As fórmulas foram escritas e conferidas no arquivo,
> mas **não foi possível testá-las dentro do Google Sheets** a partir do ambiente
> onde este material foi gerado. Rode o teste de aceitação do passo 9 antes de
> colocar em produção.

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
| Protocolos | `M2:M301` | Doc. completa? |
| Protocolos | `S2:S301` | Digitalizado? |
| Protocolos | `Y2:Y301` | Arquivado? |
| Checklist | `C2:C1001` | Entregue? |

As células já vêm com `FALSO`, então viram caixas desmarcadas.

## 4. Conferir as listas suspensas

O `.xlsx` já traz as validações. Confira em `Protocolos!I2` se aparece a seta da
lista. Se a importação tiver perdido alguma, recrie com
`Dados › Validação de dados › Adicionar regra › Menu suspenso (de um intervalo)`:

| Coluna | Intervalo de aplicação | Origem |
|---|---|---|
| E — PF/PJ | `E2:E301` | `Listas!$M$2:$M$5` |
| I — Tipo de ato | `I2:I301` | `Listas!$A$2:$A$100` |
| K — Canal | `K2:K301` | `Listas!$K$2:$K$20` |
| L — Responsável | `L2:L301` | `Listas!$I$2:$I$50` |
| R — Fase | `R2:R301` | `Listas!$D$2:$D$100` |
| W — Atualizado por | `W2:W301` | `Listas!$I$2:$I$50` |
| Checklist A — ID Protocolo | `A2:A1001` | `Protocolos!$A$2:$A$301` |

A última linha da tabela (ID do protocolo na aba Checklist) **não vem no arquivo** —
crie-a manualmente. Ela é o que evita digitar um ID que não existe.

## 5. Formatação condicional — **montar à mão, uma a uma**

Selecione o intervalo, abra `Formatar › Formatação condicional › Adicionar outra
regra`, escolha **"A fórmula personalizada é"** (é a última opção do menu suspenso,
precisa rolar) e cole a fórmula. As fórmulas abaixo já estão em pt-BR com `;`.

**Bloco principal — selecione `A2:Z301` antes de começar.** Crie nesta ordem, porque
a primeira regra que casar define o fundo da célula:

| # | Fórmula | Formato |
|---|---|---|
| 1 | `=$Y2=VERDADEIRO` | fundo cinza claro, texto cinza (arquivado) |
| 2 | `=E($R2="Finalizado";$S2=FALSO)` | fundo vermelho forte, texto branco |
| 3 | `=$Q2="Atrasado"` | fundo vermelho claro, texto vermelho escuro |
| 4 | `=$Q2="Vence hoje"` | fundo âmbar, texto laranja escuro |
| 5 | `=$Q2="Concluído"` | fundo verde claro, texto verde escuro |
| 6 | `=E($M2=VERDADEIRO;$U2<>"";$U2<1)` | sem fundo, texto âmbar em negrito |

**Regras em intervalos próprios:**

| Intervalo | Fórmula | Formato |
|---|---|---|
| `Protocolos!A2:A301` | `=E($A2<>"";CONT.SE($A$2:$A$301;$A2)>1)` | vermelho claro, negrito (ID duplicado) |
| `Protocolos!B2:B301` | `=E($B2<>"";CONT.SE($B$2:$B$301;$B2)>1)` | vermelho claro, negrito (Nº DRD duplicado) |
| `Checklist!A2:D1001` | `=$C2=VERDADEIRO` | texto cinza (documento já entregue) |

**Cor por escrevente.** Em `Protocolos!L2:L301`, uma regra por nome
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
dados do passo 4 (menu suspenso vindo de `Protocolos!$A$2:$A$301`) já sinaliza um ID
que não existe, com o mesmo efeito e sem uma regra extra.

Depois de aplicar a melhoria do passo 8, estenda os intervalos destas regras de
`301` para a coluna inteira (`A2:Z`, `A2:A`, etc.).

> Não é possível, sem Apps Script, esmaecer automaticamente "as linhas que não são
> minhas": nenhuma fórmula nativa sabe quem está com a planilha aberta. A cor por
> escrevente (coluna L) é o substituto mais próximo; a separação de verdade é a
> visualização de filtro do passo 6.

Depois de aplicar a melhoria do passo 8, estenda os intervalos destas regras de
`301` para a coluna inteira (`A2:Z`, `A2:A`, etc.).

## 6. Visualizações de Filtro — a peça central do uso simultâneo

**Selecione `A1:Z301` antes de criar cada visualização.** A visualização nasce com o
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
| `Protocolos!J2:J301` | restringir — Categoria (calculada) |
| `Protocolos!O2:Q301` | restringir — Prazo, Dias úteis restantes, Situação |
| `Protocolos!U2:U301` | restringir — % Checklist |
| Linha 1 de todas as abas | restringir |
| Resto de `Protocolos` e `Checklist` | `Mostrar um aviso ao editar` (avisa sem bloquear) |

`O2:Q301` cobre as três colunas calculadas contíguas de uma vez — não precisa de uma
proteção por coluna.

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
coluna abaixo: **apague o intervalo inteiro** (ex. `J2:J301`) e cole a fórmula
**apenas na primeira célula** (`J2`):

**J2 — Categoria**
```
=ARRAYFORMULA(SE($I$2:$I="";"";SEERRO(PROCV($I$2:$I;Listas!$A$2:$B$100;2;FALSO);"—")))
```

**O2 — Prazo**
```
=ARRAYFORMULA(SE($N$2:$N="";"";DIATRABALHO($N$2:$N;5;Listas!$O$2:$O$200)))
```

**P2 — Dias úteis restantes**
```
=ARRAYFORMULA(SE($O$2:$O="";"";SE($O$2:$O>=HOJE();DIATRABALHOTOTAL(HOJE();$O$2:$O;Listas!$O$2:$O$200)-1;DIATRABALHOTOTAL(HOJE();$O$2:$O;Listas!$O$2:$O$200)+1)))
```

**Q2 — Situação**
```
=ARRAYFORMULA(SE($O$2:$O="";"";SE($R$2:$R="Finalizado";"Concluído";SE($R$2:$R="Usuário desistiu";"Encerrado";SE($P$2:$P<0;"Atrasado";SE($P$2:$P=0;"Vence hoje";"No prazo"))))))
```

**U2 — % Checklist**
```
=ARRAYFORMULA(SE($A$2:$A="";"";SEERRO(CONT.SES(Checklist!$A$2:$A$3000;$A$2:$A;Checklist!$C$2:$C$3000;VERDADEIRO)/CONT.SE(Checklist!$A$2:$A$3000;$A$2:$A);"")))
```

Depois, ajuste também os intervalos do passo 7 e das regras do passo 5 para
`A2:Z` (coluna inteira) em vez de parar na linha 301.

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
9. **Simultâneo.** Abra com duas contas ao mesmo tempo, cada uma na sua
   visualização de filtro, e edite linhas diferentes — nenhuma deve interferir na outra.

Depois apague a linha de teste (e as linhas de checklist dela).

> O item 3 tem uma borda conhecida: se você abrir a planilha num **sábado ou
> domingo**, a contagem de dias úteis pode marcar como "vence hoje" o prazo que na
> verdade é da segunda-feira. Como o setor trabalha em dia útil, isso foi aceito
> em vez de complicar a fórmula.

## 10. Feriados — **pendente de verificação**

A aba `Listas`, coluna O, traz os feriados nacionais de 2026. Os quatro marcados
com `(CONFERIR)` são móveis e foram calculados, não consultados em fonte oficial:

| Data | Feriado |
|---|---|
| 16/02/2026 | Carnaval — segunda |
| 17/02/2026 | Carnaval — terça |
| 03/04/2026 | Sexta-feira Santa |
| 04/06/2026 | Corpus Christi |

**Confira em fonte oficial antes do uso real** e acrescente os feriados estaduais
(ES) e municipais, além de pontos facultativos que a serventia não abre (quarta-feira
de cinzas, por exemplo). Basta acrescentar linhas na coluna O — as fórmulas de prazo
já leem até a linha 200.

**Todo o cálculo dos 5 dias úteis depende dessa lista.** É o item de maior risco
da migração.

## 10-A. Levar a planilha pronta para o Workspace do cartório

Não é preciso remontar nada. `Arquivo › Fazer uma cópia` carrega fórmulas,
formatação condicional, validação de dados, caixas de seleção, intervalos nomeados,
visualizações de filtro e as configurações de local e fuso.

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
| Local e fuso | Reconferir — já veio errado uma vez nesta montagem |
| Visualizações de filtro | Devem vir na cópia; se faltarem, recrie pelo passo 6 |
| Feriados | Continuam pendentes de verificação, independentemente da cópia |

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
3. **Formatação condicional** — em `Protocolos!L2:L301`, edite as 3 regras de cor por
   escrevente (passo 5) trocando o nome dentro de cada fórmula.
4. **Visualizações de filtro** — em cada uma das 3 `Minhas — …` (passo 6), renomeie a
   visualização e ajuste a condição de texto. Renomear a visualização **não** muda o
   critério; são duas edições separadas.
5. **`Painel`, coluna B, linhas 26 a 28** — troque os nomes. As fórmulas ao lado
   referenciam `$B$26`, `$B$27` e `$B$28`, então basta trocar o texto da célula.
   A aba está protegida; desproteja, edite e proteja de novo.

**Para acrescentar uma quarta escrevente**, além dos passos acima: adicione o nome em
`Listas!I5`, crie a visualização de filtro `Minhas — <nome>`, e copie a linha 28 do
`Painel` para a 29 ajustando as referências. As validações de dados não precisam de
ajuste — já leem `Listas!$I$2:$I$50`.

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
