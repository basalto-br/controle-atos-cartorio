# Dados de demonstração

Protocolos fictícios para apresentar a ferramenta sem abrir uma tela vazia na
frente de um tabelião.

**Nenhum dado é real.** Nomes, telefones, documentos, valores e empresas são
inventados. Nada aqui saiu de serventia nenhuma — e nada real pode entrar, porque
este repositório é público.

## Como usar

1. Abra **`controle-atos-cartorio.pages.dev`** no navegador.
2. Clique em **"Carregar dados de demonstração"**, no meio da tela vazia.

Só isso. Não há arquivo para baixar, nem seletor de arquivo, nem nada a preparar
antes — inclusive na máquina de outra pessoa, que é justamente o caso em que
baixar um `.json` desconhecido seria constrangedor ou bloqueado.

O mesmo botão fica em **⚙ Configurações → Demonstração**, para recarregar depois
que já houver dados na tela. Aí ele pede confirmação, porque substitui tudo.

## Onde a demonstração roda

Em `controle-atos-cartorio.pages.dev`, que serve a mesma `main` que a produção mas
**não é** produção: como o host não é `app.ritonotas.com.br`, o app entra em modo
de teste sozinho — faixa vermelha no topo, `[TESTE]` no título da aba e chave de
armazenamento separada.

O servidor local (`.claude/serve.ps1`, porta 8123) tem o mesmo comportamento e roda
sem internet, o que protege contra o wi-fi do cartório visitado.

**Em `app.ritonotas.com.br` o botão não existe.** Não é escondido: não é
renderizado, e a função recusa mesmo se alguém a chamar pelo console. A trava é
`IS_PROD`, a mesma que governa a faixa vermelha e a chave de armazenamento.

## Não fica nada na máquina

Sem pasta de dados conectada, o app guarda tudo **em memória** — fechou a aba,
acabou. Nada em disco, nada no `localStorage`, nada no IndexedDB, e os backups
automáticos nem chegam a rodar.

Isso é o que torna seguro demonstrar no computador do próprio cartório visitado. E
serve de argumento na conversa: dá para recarregar a página na frente do tabelião e
mostrar que não sobrou nada — o que demonstra, de graça, a promessa central do
produto.

O outro lado da moeda: a demonstração precisa ser carregada de novo a cada aba
nova. Como é um clique, não incomoda.

## O que cada protocolo mostra

São 16, e cada um exercita uma regra diferente. Ao editar a lista, veja o que está
apagando — vários são o único caso que exercita o que exercitam. Cada entrada tem
um campo `mostra`, no código, dizendo para que serve.

| Protocolo | O que demonstra |
|---|---|
| Helena Vasconcelos Prado | Documentação incompleta: o prazo ainda nem começou a contar |
| Otávio Camargo Lins | Fase que depende do usuário — o relógio corre, mas não acusa atraso |
| Beatriz Nogueira Sampaio | Vence hoje |
| Transportadora Vale Norte | **Atrasado de verdade**, com a demora do próprio cartório |
| Joana Ferraz Coutinho | Checklist longo pela metade, com agenda de pendências |
| Ricardo Malheiros Fontes | Minuta em conferência pelo usuário |
| Eduarda Pimentel Rocha | Certidão de ônus a vencer, dentro do aviso de 5 dias |
| Gustavo Freire Antunes | Certidão de ônus **vencida** — precisa de uma nova |
| Construtora Pedra Branca | Exige ônus e a data de emissão ainda não foi informada |
| Sônia Rezende Vilela (2) | Par vinculado: mesma pessoa, dois atos, um já finalizado |
| Padaria Dois Irmãos | Finalizado mas **não digitalizado** — ainda não pode arquivar |
| Ana Lúcia Barcelos Pinto | Fase final que não exige digitalização |
| Henrique Salgado Moreira | No prazo, folgado. O caso comum precisa aparecer também |
| Cláudia Bethânia Aragão | Atrasada, mas a demora foi do usuário — o rótulo do prazo atribui a espera |
| "Lançamento duplicado" | Lixeira: excluir nunca apaga, só move |

Fora dos protocolos: três responsáveis, três tarefas no painel (uma com checklist
de anotação no livro, um substabelecimento de outra serventia e uma tarefa livre),
e doze dias úteis de atos de balcão para o gráfico ter forma.

## Onde mexer

Tudo vive no `controle-atos.html`, na seção **"Dados de demonstração"**, logo antes
de "Persistência". Para mudar a lista, edite `demoEspecificacoes()`.

Três decisões que valem conhecer antes de alterar:

**É gerador, não arquivo.** As datas são calculadas na hora, relativas ao dia em
que se clica, então a demonstração nunca envelhece. Um arquivo fixo mostraria tudo
atrasado depois de uma semana — a impressão contrária à que se quer causar.

**Usa `addBusinessDays` e `isBusinessDay` do próprio app.** Não há um segundo
calendário de feriados para divergir em silêncio. Uma versão anterior deste
material era um script em Python que espelhava esse cálculo; foi removida
justamente por isso.

**A âncora é o próximo dia útil quando hoje não é.** Cartório não abre no fim de
semana. Sem isso, num domingo o protocolo que deveria "vencer hoje" venceria só na
segunda, e os deslocamentos de 0 e de 1 dia útil cairiam na mesma data.

**`statusList` fica fora do estado gerado**, de propósito. Sem a chave, `migrate()`
semeia as 8 fases padrão; fixá-la congelaria a demonstração numa versão antiga
assim que alguém editasse `DEFAULT_STATUS_LIST`.
