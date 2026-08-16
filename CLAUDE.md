# Controle de Atos — Protocolos (Cartório de Notas)

Ferramenta de controle de protocolos de atos notariais (procurações públicas e
escrituras) para um tabelião/escrevente. Cada protocolo tem prazo, status de
andamento e histórico. Uso diário, em dias úteis, por um escrevente de cartório.

## Rumo do produto (contexto comercial)

A ferramenta vai virar produto vendido a cartórios, como app web multiusuário. Esta
seção existe para dar contexto às decisões — **o resto do arquivo descreve o que a
ferramenta é hoje, e continua valendo.**

### O que já é verdade hoje

- Uso individual, dados locais, um usuário por instalação.
- Hospedagem na **Cloudflare Pages**, em `app.ritonotas.com.br`. Repositório na
  organização `basalto-br` — ver "Publicação", no Fluxo de trabalho.
- Ambiente detectado por hostname em tempo de execução (`HOST_PRODUCAO` / `IS_PROD`):
  qualquer host que não seja o de produção é ambiente de teste, com chave de
  armazenamento e arquivo de dados separados.

### Para onde vai — **não implementar nada disso sem o usuário pedir explicitamente**

- Nuvem com Supabase, região São Paulo; Postgres com RLS isolando por serventia.
- A conta principal pertence à **serventia** (identificada pelo CNS), nunca ao CPF do
  tabelião — delegação muda de titular por morte, aposentadoria ou concurso.
- Papéis: Titular, Administrador, Escrevente. A lixeira que já existe é o modelo de
  permissão: escrevente manda para a lixeira, só Administrador e Titular esvaziam.
- Setores são conjuntos nomeados de tipos de ato, opcionais, com padrão "Geral"
  invisível na interface enquanto houver só um.
- Regra de visibilidade: vê tudo do cartório, edita só o do próprio setor.

### Restrições que valem desde já

- Continuar em arquivo único. Não dividir em módulos.
- `migrate()` roda em todo carregamento e é a única função capaz de destruir protocolo
  real — toda alteração nela é testada contra cópia de arquivo antigo de verdade.
- Nenhum dado de protocolo real vai para o repositório, em nenhuma branch.
- A chave `service_role` do Supabase **nunca** entra no repositório, nem se ele for
  privado. A `anon` pode, porque é pública por desenho e quem protege é o RLS.
- Não iniciar a migração para nuvem por conta própria: ela tem plano e mês próprios.

## Stack e comandos

- **Arquivo único `controle-atos.html`** — HTML + CSS + JS puro, sem framework, sem
  build, sem bundler. `index.html` só redireciona pra ele (é a entrada da hospedagem
  estática).
  **Nunca dividir em módulos/arquivos separados sem perguntar antes**, mesmo em
  refatorações grandes.
- **Sem testes automatizados** — verificação é manual, no navegador.
- **Rodar localmente**: servidor de dev é PowerShell puro (`.claude/serve.ps1`,
  config `.claude/launch.json`, nome `controle-atos`, porta 8123) →
  `http://localhost:8123/controle-atos.html` — não usa Node nem nenhum bundler.
  (Node foi instalado nesta máquina depois, só para os MCPs de `github`/`perplexity`,
  não para o servidor de dev.)
- **Deploy**: push em `main` publica direto via Cloudflare Pages, projeto
  `controle-atos-cartorio` em `basalto-br/controle-atos-cartorio` → `app.ritonotas.com.br`.
  Sem comando de build, servindo a raiz. Sem CI/CD.
- Fontes embutidas em base64 no `<style>` — app não faz nenhuma requisição de rede
  depois de carregar (requisito de privacidade/LGPD; dados nunca saem do PC do usuário).

## Estrutura do projeto

- `controle-atos.html` — app inteiro (dados, lógica, render, estilo).
- `index.html` — redirect estático pra `controle-atos.html`.
- `demo/LEIA-ME.md` — como usar os dados de demonstração. **Os dados em si não
  são arquivo**: são gerados em JavaScript, na seção "Dados de demonstração" do
  `controle-atos.html`, logo antes de "Persistência". Editar a lista =
  `demoEspecificacoes()`. Travado em `!IS_PROD`: em `app.ritonotas.com.br` os
  botões não são renderizados e `App.carregarDemonstracao` recusa.
- **Não manter um mapa de linhas do arquivo** (já foi tentado com um
  `ARCHITECTURE.md` e removido) — reconferir as faixas a cada mudança de tamanho
  do arquivo custava um agente inteiro relendo tudo, mais caro do que o que
  economizava. Usar `Grep` pontual (por nome de função/comentário) pra navegar —
  funciona bem e nunca fica desatualizado.
- `design_handoff_protocolos/` (pasta irmã, fora do repo) — referência visual do
  redesign já implementado; só consultar se surgir dúvida de intenção de design.

## Persistência (3 camadas, nesta ordem de preferência)

1. **Pasta local** (File System Access, Chrome/Edge) — `App.conectarPastaDados`.
   Salva em `FS_DATA_FILE` a cada mudança (`fsFlush`, coalescido) + backups 2×/dia
   (10:50 e 17:45) numa subpasta `backups/`.
2. **`window.storage`** (API de artifact do Claude.ai) — fallback sem pasta
   conectada. Sem os dois, cai em memória (perde tudo ao fechar a aba).
3. **Backup/restauração manual** (`.json` do `state` inteiro) — rede de segurança;
   nunca remover essa opção.

`migrate(raw)` roda em **todo** carregamento e preenche campos ausentes sem quebrar
dados salvos. Todo caminho que gera um `state` novo precisa passar por `migrate()`
(já houve bug de fallback pulando isso — ver Armadilhas).

## Modelo de dados (`state`)

- `protocolos`: array de atos. Campos: `id`, `numeroProtocolo`, `cliente` (nome —
  ver nota de terminologia em Convenções), `clienteTelefone`, `clienteEmail`,
  `outorgados`, `responsavel` (string única), `tipoPessoa` (`pf`/`pj`), `canais`
  (array), `dataProtocolo`, `docsCompletos`, `dataRecebimentoCompleto`, `status`,
  `tipos` (array de strings), `observacoesHistorico` (`{texto, ts, etiqueta?,
  editadoEm?}`), `historico` (`{status, ts}`, imutável), `rascunhoDigitalizado`,
  `dataDigitalizacao`, `grupoVinculoId`, `documentosMarcados` (mapa doc→bool),
  `documentosExtras` (array), `pendencias` (array, ver Regras), `naLixeira`,
  `dataExclusao`, `createdAt`.
- `tiposAtos`: array de strings. `categoriaPorTipo`: mapa
  nome→`'procuracao'|'escritura'|null`, classificado por prefixo
  (`categorizarTipoPorNome`); sem match fica `null` de propósito, nunca um palpite.
- `checklistPorTipo`: mapa nome-do-tipo→documentos específicos, somado à base fixa
  `DOCUMENTOS_BASE_CHECKLIST` via `getChecklistDoProtocolo(p)`.
- `statusList`: fases de andamento — ver seção própria abaixo.
- `responsaveis`: array de nomes pré-definidos (reaproveitado no responsável das
  pendências). `feriadosExtras`/`feriadosMoveis`: cálculo de prazo e da agenda.
- `atosBalcao`: `{data: quantidade}`. `atosBalcaoLancamentos`: `{data: [{qtd,ts}]}`
  (só incremento positivo vira lançamento).
- `sugestoesDispensadas`: pares de ids marcados "não é a mesma pessoa" no vínculo.
- `documentosChecklist`: campo legado, não editável mais pela UI — mantido intacto
  no `state` só por preservação de dado antigo.

## Regras de negócio (não quebrar sem o usuário pedir)

- **Prazo fixo de 5 dias úteis** (`PRAZO_DIAS_UTEIS`), contado da documentação
  completa, descontando fins de semana/feriados. Sem exceção por tipo de ato.
- **PF/PJ**: selo na ficha + filtro + opção de agrupar em seções — as três formas
  coexistem, nenhuma substitui a outra.
- **Responsável**: sempre um só por protocolo, seleção única.
- **Lixeira, nunca exclusão direta**: excluir só marca `naLixeira=true`; excluir de
  vez é ação separada, sempre com confirmação.
- **Atos de balcão**: contador por dia, sem protocolo associado, dado totalmente
  separado de `protocolos`.
- **Arquivamento**: status `isFinal` E (não exige digitalização OU
  `rascunhoDigitalizado===true`). Só "Finalizado" exige digitalização por padrão.
- **Vínculo entre protocolos** é sempre manual — sugestão por nome é só atalho,
  nunca vincula sozinho.
- **Checklist de documentos** nunca marca "documentação completa" sozinho — dois
  controles manuais independentes.
- **Agenda de pendências** (`p.pendencias`) fica separada de observações/histórico
  de status no armazenamento — criação/conclusão aparecem juntas numa timeline
  unificada só como espelho de leitura (`buildTimelineUnificada`), nunca duplicar
  ou misturar os dados de origem.

## Fases de andamento (`statusList`)

Definidas em `DEFAULT_STATUS_LIST`, perto do topo do arquivo. Cada fase:
`{key, label, cor, isFinal, requerDigitalizacao}` — `cor` é uma chave de `PALETTE`
(gray/gold/blue/plum/green/dark/teal/rose). Totalmente editável pelo usuário em
Configurações (adicionar/editar/reordenar/remover).

Ordem atual (8 fases): Aguardando documentos p/ análise → Pendência de documentos →
Em confecção → Em análise pelo Tabelião → Em conferência pelo usuário → Aguardando
assinatura → Finalizado (final, exige digitalização) → Usuário desistiu (final).

**Pra adicionar uma fase nova sem quebrar instalações já em uso**: usar
`inserirFaseAposChave(lista, afterKey, novaFase)` — insere pela `key` (estável,
nunca editada pelo usuário), é idempotente, e cai pra "acrescenta no fim" se a
âncora não existir mais. Nunca sobrescrever um `label` que o usuário já customizou.

## Convenções de código

- Tudo dentro de uma IIFE, sem módulos/import/export.
- Views são `renderX()` que retornam strings HTML, injetadas via `innerHTML`. Ações
  do usuário são métodos em `App.*`, chamados por `onclick="App.xxx(...)"` inline.
- Toda mudança de estado passa por `App.render()` → `withFocus(renderAll)`, que
  reconstrói `#app.innerHTML` inteiro e restaura foco/seleção/scroll depois.
- Campos de texto usam `oninput` → `App.setField()`, que só atualiza o rascunho
  **sem** re-renderizar; outros controles (select/chip/checkbox) chamam funções que
  já re-renderizam.
- Nomenclatura em português (funções, variáveis, comentários).
- Nomes internos (`p.cliente`, `App.showClienteHistory`) ficam "cliente" por
  herança histórica; todo texto **visível na UI** usa "usuário".
- **"Livro" não descreve a ferramenta.** Em serventia é termo de arte com peso legal
  (Livro de Notas, Livro Protocolo) e usá-lo para o produto cria ambiguidade sobre
  escopo — a ferramenta acompanha andamento, não é livro de nada. O `<h1>` já foi
  "Livro de Protocolos" e virou "Controle de Protocolos"; os `<title>` viraram
  "Controle de Atos — Protocolos".
  **Mas "livro" continua certo quando é o livro de verdade:** a tarefa "Anotar no
  livro", a chave `anotar_livro`, o campo `numeroLivro` / "Nº do livro" e os textos
  sobre averbação e aditamento nos livros descrevem o Livro de Notas real. Não troque
  esses — é exatamente o termo que a regra existe para preservar.
  A mesma regra vale na landing (`site-ritonotas/CLAUDE.md`, "O que não fazer").
- Visual: tokens CSS em `:root` (`--painel`, `--ficha`, `--apoio`, etc.) e famílias
  de classe por tela (`.cp*` ficha, `.kb-*` kanban, `.fm-*` formulário, `.vp-*`
  vínculo, `.ab-*` atos de balcão, `.lx-*` lixeira). Usar os tokens existentes em
  vez de cor solta; detalhe completo em `design_handoff_protocolos/`.

## Armadilhas conhecidas

- **Campo de texto perdendo valor**: nunca re-renderizar a cada tecla — só
  `oninput` → `App.setField()` sem render.
- **`App.saveProtocolo` apagando campo não editável na tela atual**: o `payload`
  sempre herda de `original.campo` os campos que aquele formulário não edita.
- **Animação incondicional** em elemento recriado a cada render (ficha, cartão do
  kanban) causa "piscar" a tela toda — usar flags de disparo único
  (`justOpenedKey`, `justCreatedId`, `modalJustOpened`).
- **Dirty-check falso positivo** no painel de criar/editar (`isDraftDirty()`):
  tirar o snapshot só depois de `captureModalTextFields()`; ao revelar campo com
  valor padrão (expandir opcionais, trocar categoria), medir dirty *antes* de mudar
  e só atualizar o snapshot se ainda não estava sujo.
- **`array.map(nomeDeFuncao)` com a função tendo 2º parâmetro**: `map` passa
  `(item, index, array)` — todo item a partir do índice 1 recebe o índice errado
  nesse parâmetro. Sempre envolver: `arr.map(function(x){return fn(x);})`.
- **Heurística de nome com acento** (`categorizarTipoPorNome`): remover acentos
  antes de comparar prefixo — "ç"/"ã" podem estar em normalização Unicode NFC ou
  NFD, e `indexOf` ingênuo falha silenciosamente.
- **Vínculo manual duplica lógica de merge** (`applyVinculoManual` vs.
  `App.saveProtocolo`) de propósito — o payload do formulário ainda não está em
  `state.protocolos` no momento do merge dentro de `saveProtocolo`; compartilhar um
  helper seria arriscado sem re-testar os dois caminhos.

## Fluxo de trabalho

Branch por feature/fix (`feat/xxx` ou `fix/xxx`) → implementar e testar no navegador →
commit em português, em passos pequenos e descritivos (`Co-Authored-By: Claude`) →
push → abrir PR com `gh pr create` resumindo a mudança → usuário revisa e pede
"mescla e continua" → merge → apagar a branch local e remota. **Nunca commitar direto
na `main`.** Sem CI — testar manualmente antes de cada commit.

### Publicação (a `main` é produção)

- **Todo merge vai ao ar na hora.** A Cloudflare Pages publica a `main` em
  **`https://app.ritonotas.com.br`** (ver "Deploy", em Stack e comandos). Não existe
  etapa de aprovação depois do merge — **o merge *é* o deploy**. Mesclar um PR e "ver
  depois se ficou bom" não é uma opção.
- **Existem duas verificações antes da produção, e as duas importam.**

  1. **O servidor local** (porta 8123). Rápido, é onde se testa comportamento. Continua
     não sendo opcional.
  2. **A URL de preview da branch**, que a Cloudflare gera sozinha a cada push fora da
     `main`: `https://<branch>.controle-atos-cartorio.pages.dev`. É a única forma de
     testar o que só existe na Cloudflare — em especial o `_headers`, que o servidor
     local não aplica. Confirmado: a CSP vem na resposta do preview.

  O alias da branch é o nome com tudo que não é letra ou número virando `-`, **truncado
  em 28 caracteres**. `fix/doc-github-pages-desligado` (30) vira
  `fix-doc-github-pages-desliga` (28). Consultar o nome inteiro devolve 404 e parece que
  o preview não existe.

  A branch de produção **não** ganha alias: `main.controle-atos-cartorio.pages.dev` dá
  404, porque a `main` é servida na raiz do projeto e em `app.ritonotas.com.br`.

  O preview roda **em modo de teste** — o host não é `app.ritonotas.com.br`, então a
  detecção por hostname já separa o armazenamento. Testar no preview não toca no dado
  real.
- **Rollback = `git revert` do merge + push.** Reverter o commit de merge na `main` e
  empurrar; o Pages republica sozinho. **Nunca `git reset` nem force-push na `main`** —
  o histórico da produção tem que continuar auditável.
- **O app detecta o ambiente por hostname**: `HOST_PRODUCAO` e `IS_PROD`, no bloco de
  script do cabeçalho. Qualquer host diferente do de produção entra em modo de teste —
  faixa vermelha, `[TESTE]` no título, e chave de armazenamento e arquivo de dados
  separados. Testar fora da produção nunca toca no dado real.
- **`HOST_PRODUCAO` vale `app.ritonotas.com.br`.** Só nesse endereço o app se trata
  como produção. Qualquer outro — `localhost`, `*.pages.dev` — entra em modo de teste,
  com armazenamento separado.

  **Trocar essa constante troca a chave dos dados**, e é por isso que ela foi acertada
  antes de existir protocolo real:

  | | Teste | Produção |
  |---|---|---|
  | `STORAGE_KEY` | `cartorio-data-TESTE` | `cartorio-data` |
  | `FS_DATA_FILE` | `controle-atos-dados-TESTE.json` | `controle-atos-dados.json` |
  | `FS_BACKUP_DIR` | `backups-TESTE` | `backups` |

  Mudá-la depois que o cartório já lançou protocolo faz os dados **sumirem da tela** —
  continuam salvos, mas sob a chave antiga. Se algum dia o domínio mudar, migre o
  conteúdo da chave antes de trocar a constante.

**A migração para Cloudflare Pages aconteceu em 16/08/2026.** Os dois repositórios
(ferramenta e site) estão na organização `basalto-br`, e o projeto Pages
`controle-atos-cartorio` publica a `main` em `app.ritonotas.com.br`, sem comando de
build e servindo a raiz.

**O GitHub Pages foi desligado**, e com isso a migração está fechada. Enquanto esteve
ligado, `https://basalto-br.github.io/controle-atos-cartorio/` servia a mesma `main`:
duas cópias públicas do app, das quais só a da Cloudflare era produção. Era uma forma
fácil de alguém lançar protocolo no lugar errado. Hoje esse endereço responde 404, e
existe uma cópia pública só.
