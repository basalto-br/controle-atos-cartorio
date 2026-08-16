# Dados de demonstração

Protocolos fictícios para apresentar a ferramenta sem abrir uma tela vazia na
frente de um tabelião.

**Nenhum dado é real.** Nomes, telefones, documentos, valores e empresas são
inventados. Nada aqui saiu de serventia nenhuma — e nada real pode entrar, porque
este repositório é público.

## Como usar

**1. Gere os dados no dia da conversa.**

```bash
python demo/gerar-dados-demo.py
```

As datas são relativas ao dia em que o script roda. Um arquivo gerado há duas
semanas mostra tudo atrasado — que é a impressão oposta da que se quer passar. Se
o dia não for útil, o script ancora tudo no próximo dia útil e avisa na saída.

**2. Abra a ferramenta em `controle-atos-cartorio.pages.dev`.**

Esse endereço serve a mesma `main` que a produção, mas **não é** produção: como o
host não é `app.ritonotas.com.br`, o app entra em modo de teste sozinho — faixa
vermelha no topo, `[TESTE]` no título da aba e armazenamento separado
(`cartorio-data-TESTE`).

A faixa vermelha aparece na demonstração. Se atrapalhar, o servidor local
(`.claude/serve.ps1`, porta 8123) tem o mesmo comportamento e roda sem internet —
o que também protege contra o wi-fi do cartório visitado.

**3. Importe `demo/dados-demo.json`** em Configurações → Backup → Importar.

> **A importação substitui tudo.** É inofensivo no armazenamento de teste, que
> existe para isso. **Nunca faça isso em `app.ritonotas.com.br`** — lá apagaria
> protocolo real do cartório, e não há como desfazer.

Feito uma vez, os dados ficam no navegador daquela máquina. Só é preciso repetir
em computador novo, ou quando quiser as datas atualizadas.

## O que cada protocolo mostra

Cada um exercita uma regra diferente. Ao editar a lista, veja o que está apagando —
vários são o único caso que exercita o que exercitam.

| Protocolo | O que demonstra |
|---|---|
| Helena Vasconcelos Prado | Documentação incompleta: o prazo ainda nem começou a contar |
| Otávio Camargo Lins | Fase que depende do usuário — o relógio corre, mas não acusa atraso |
| Beatriz Nogueira Sampaio | Vence hoje |
| Transportadora Vale Norte | **Atrasado de verdade** — o único vermelho legítimo da tela |
| Joana Ferraz Coutinho | Checklist longo pela metade, com agenda de pendências |
| Ricardo Malheiros Fontes | Minuta em conferência pelo usuário |
| Eduarda Pimentel Rocha | Certidão de ônus a vencer, dentro do aviso de 5 dias |
| Gustavo Freire Antunes | Certidão de ônus **vencida** — precisa de uma nova |
| Construtora Pedra Branca | Exige ônus e a data de emissão ainda não foi informada |
| Sônia Rezende Vilela (2) | Par vinculado: mesma pessoa, dois atos, um já finalizado |
| Padaria Dois Irmãos | Finalizado mas **não digitalizado** — ainda não pode arquivar |
| Ana Lúcia Barcelos Pinto | Fase final que não exige digitalização |
| Henrique Salgado Moreira | No prazo, folgado. O caso comum precisa aparecer também |
| "Lançamento duplicado" | Lixeira: excluir nunca apaga, só move |

Fora dos protocolos: três responsáveis, três tarefas no painel (uma com checklist
de anotação no livro, um substabelecimento de outra serventia e uma tarefa livre),
e doze dias úteis de atos de balcão para o gráfico ter forma.

## Sobre o gerador

O arquivo de saída é exatamente o que `App.exportBackup` grava: o objeto `state`
inteiro. Entra pelo mesmo caminho de importação de backup e passa por `migrate()`,
então campo ausente aqui é preenchido lá.

`statusList` fica **de fora de propósito**. Sem a chave, `migrate()` semeia as 8
fases padrão. Fixá-la aqui congelaria a demonstração numa versão antiga das fases
assim que alguém editasse `DEFAULT_STATUS_LIST`.

O cálculo de dias úteis e o calendário de feriados são espelhados do
`controle-atos.html`. Se os feriados mudarem lá, mudem aqui também — o prazo de 5
dias úteis depende dos dois concordarem, e o desencontro só apareceria como uma
data estranha na tela, sem erro nenhum.
