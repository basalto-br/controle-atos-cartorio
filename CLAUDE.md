# Livro de Protocolos — Controle de Atos (Cartório de Notas)

Ferramenta de controle de protocolos para um tabelião/escrevente de Cartório de Notas
(procurações públicas e escrituras). Arquivo único `controle-atos.html` — HTML + CSS +
JavaScript puro (sem framework, sem build), pensado para rodar como um artifact do
Claude.ai (usa a API `window.storage` para persistência) e também localmente, em
qualquer navegador.

## Quem usa e por quê

O usuário é escrevente de cartório, bacharel em direito, que redige procurações
públicas e escrituras e analisa capacidade jurídica de empresas a partir de contratos
sociais. Usa a ferramenta todo dia útil para controlar prazos, status e documentação
de cada ato. Está no plano Pro do Claude.

## Arquitetura (importante preservar)

- **Um arquivo só**, sem **nenhuma** dependência externa. As fontes (Source Serif 4,
  Inter, JetBrains Mono) são **embutidas em base64** (`@font-face` no topo do `<style>`,
  só o subconjunto `latin`, que cobre o português) — o app não faz nenhuma requisição de
  rede depois de carregar (requisito de privacidade/LGPD; ver o dossiê e a pasta
  `design_handoff_protocolos`).
- **Sem framework**: tudo é montagem de strings HTML (`renderX()` retornam strings)
  injetadas via `innerHTML`. Não introduzir React/Vue sem discutir antes — o app atual
  depende de re-renderizações completas e handlers inline (`onclick="App.xxx(...)"`).
- **Re-render total a cada mudança de estado**: `App.render()` chama `withFocus(renderAll)`,
  que reconstrói `#app.innerHTML` inteiro. `withFocus` restaura o elemento em foco e a
  seleção de texto, **e também a posição de rolagem** de `window` e dos containers com
  rolagem própria (`SCROLL_CONTAINER_SELECTORS`: `.overlay`, `.side-panel-body`,
  `.fm-edit-col-left`, `.fm-edit-col-right`) — sem isso, qualquer clique em
  select/chip/checkbox (que dispara render) fazia a tela "pular" pro topo. Ao criar um
  novo container com rolagem própria, adicionar o seletor nessa lista. Isso já causou
  outros bugs sutis também (ver seção "Armadilhas" abaixo) — qualquer novo campo de
  texto/interação precisa levar tudo isso em conta.
- **Persistência (3 camadas que coexistem, nesta ordem de preferência):**
  1. **Pasta local via File System Access** (Chrome/Edge): o usuário conecta uma pasta
     (`App.conectarPastaDados`, guardada num `FileSystemDirectoryHandle` no IndexedDB).
     Dentro dela o app mantém o arquivo de dados ao vivo (`FS_DATA_FILE`) — salvo a cada
     mudança via `fsFlush` (com coalescência) — e uma subpasta `backups/` com cópias
     datadas geradas **2×/dia** (`FS_BACKUP_SLOTS = 10:50 e 17:45`), com "recuperação na
     próxima abertura" (`checkScheduledBackups`, marcadores no `localStorage`, retenção
     `FS_BACKUP_RETENTION_DIAS`). O navegador exige um gesto por sessão para reautorizar
     (estado `reconnect`). Só ativa em navegadores Chromium; há degradação graciosa.
  2. **`window.storage.get/set`** (API de artifacts do Claude.ai), usado como fallback
     quando nenhuma pasta está conectada. Sem ele (fora do Claude.ai), cai em memória.
  3. **Backup/restauração manual** (baixar/ler um `.json` com o `state` inteiro) como
     rede de segurança — o usuário já teve problemas reais com o artifact publicado não
     atualizar sozinho, então **não remover o backup manual**.
  Banner de status no topo (`renderFsBanner`) reflete a camada ativa. Contexto de
  implantação: dev no notebook, uso diário no PC do trabalho (Chrome); dados **locais,
  sem nuvem** (LGPD/sigilo). App servido pelo GitHub Pages; dados nunca saem do PC.
- **Migração**: a função `migrate(raw)` roda a cada carregamento e preenche campos que
  não existiam em versões antigas do `state`, sem quebrar dados já salvos. Sempre que
  adicionar um campo novo ao `state` ou a um protocolo, adicionar o default
  correspondente em `migrate()`. **Todo caminho que produz um `state` novo precisa
  passar por `migrate()`** — `loadState()` já teve um bug real em que os 3 caminhos de
  fallback (sem dado salvo, JSON inválido, promise rejeitada) chamavam `defaultState()`
  direto, pulando `migrate()` e deixando defaults calculados lá (ex.: a heurística de
  categoria de tipo) sem rodar numa instalação nova.
  Para inserir uma fase padrão nova no meio de um `statusList` que o usuário já pode
  ter customizado, usar `inserirFaseAposChave(lista, afterKey, novaFase)` — insere pela
  `key` (nunca editada pelo usuário, ao contrário do `label`), é idempotente, e cai
  para "acrescenta no fim" se a fase-âncora já tiver sido removida. Renomear um label
  padrão (ex.: "Cliente desistiu" → "Usuário desistiu") só deve sobrescrever se o label
  atual ainda for **exatamente** o texto antigo — nunca mexer num label que o usuário
  já personalizou.

## Modelo de dados (`state`)

- **`protocolos`**: array de atos. Campos principais: `id`, `numeroProtocolo`,
  `cliente`, `clienteTelefone`, `clienteEmail`, `outorgados`, `responsavel`,
  `tipoPessoa` (`pf`/`pj`), `canais` (array — um protocolo pode ter vários canais de
  atendimento), `dataProtocolo`, `docsCompletos`, `dataRecebimentoCompleto`, `status`,
  `tipos` (array de tipos de ato), `observacoesHistorico` (array `{texto, ts, etiqueta,
  editadoEm}` — `etiqueta` é uma das chaves de `ETIQUETAS_OBS`, opcional; `editadoEm`
  marca quando uma entrada foi corrigida via `App.confirmarCorrecaoObs`, nunca some o
  texto original), `historico` (array `{status, ts}` — toda mudança de status fica
  registrada com data/hora), `rascunhoDigitalizado`, `dataDigitalizacao`,
  `grupoVinculoId` (vínculo manual com outros protocolos), `documentosMarcados` (mapa
  texto-do-documento → `true`, ver checklist abaixo), `documentosExtras` (array de
  strings, documentos ad-hoc só deste protocolo), `pendencias` (array, ver agenda
  abaixo), `naLixeira`, `dataExclusao`, `createdAt`.
  Apesar do nome do campo (`cliente`) e das funções internas (`App.showClienteHistory`
  etc.) continuarem `cliente*` por herança histórica, **todo texto visível na
  interface usa "usuário"** ("Nome do usuário / outorgante", etc.) — não confundir um
  com o outro; renomear os identificadores internos foi avaliado e descartado por ser
  um refactor de alto risco sem ganho visível.
- **`tiposAtos`**: lista (array de strings) de tipos de procuração/escritura, editável
  em Configurações. **`categoriaPorTipo`**: mapa `nome-do-tipo → 'procuracao' |
  'escritura' | null`, mantido **fora** de `tiposAtos` de propósito (tipos são sempre
  referenciados pelo nome-string em todo o resto do código; não virar `{nome,
  categoria}` só por causa disso). `categorizarTipoPorNome(nome)` classifica
  automaticamente por prefixo do nome (`normalizarSemAcento` primeiro, pra não falhar
  por causa de normalização Unicode NFC/NFD do "ç"/"ã"); quem não bate com nenhum
  prefixo fica `null` de propósito — o usuário classifica manualmente em
  Configurações, nunca um palpite forçado.
- **`checklistPorTipo`**: mapa `nome-do-tipo → array de documentos específicos`. Some
  a `DOCUMENTOS_BASE_CHECKLIST` (constante fixa, não editável, vale pra todo tipo) via
  `getChecklistDoProtocolo(p)`, que também soma `p.documentosExtras` — tudo
  deduplicado, sem repetir item. Marcar um documento (`documentosMarcados`) nunca marca
  "documentação completa" automaticamente — são dois controles manuais independentes.
  Um extra ad-hoc pode ser "promovido" (`App.promoverDocumentoExtra`) pra virar
  documento padrão do tipo escolhido: entra em `checklistPorTipo`, sai de
  `documentosExtras` daquele protocolo, e a marcação de "recebido" nunca se perde nesse
  processo. O campo antigo `documentosChecklist` (lista global única, pré-existente a
  este sistema) continua no `state` intacto por preservação de dado, mas a tela de
  Configurações não edita mais ele.
- **`statusList`**: fases de andamento, **totalmente configuráveis pelo usuário**
  (adicionar, editar, reordenar, remover). Cada fase tem `{key, label, cor, isFinal,
  requerDigitalizacao}`. `cor` é uma das chaves de `PALETTE` (gray/gold/blue/plum/
  green/dark/teal/rose) e corresponde a variáveis CSS com o mesmo nome. Default atual
  (8 fases, nesta ordem): Aguardando documentos p/ análise → Pendência de documentos →
  Em confecção → Em análise pelo Tabelião → Em conferência pelo usuário → Aguardando
  assinatura → Finalizado (final, exige digitalização) → Usuário desistiu (final).
- **`responsaveis`**: lista de nomes pré-definidos (editável), usada como `<select>` no
  formulário — não é texto livre. `ultimoResponsavel` guarda o último usado, que vira
  padrão ao abrir "+ Novo Protocolo". A mesma lista é reaproveitada no campo
  "responsável" das pendências da agenda.
- **`feriadosExtras`** / **`feriadosMoveis`**: configuração de feriados para o cálculo
  de prazo — e também usados pela janela de dias úteis da agenda (`addBusinessDays`).
- **`atosBalcao`**: `{ 'YYYY-MM-DD': quantidade }` — contador simples de atos que não
  geram protocolo (atendimento só de balcão). Completamente separado dos protocolos.
- **`atosBalcaoLancamentos`**: `{ 'YYYY-MM-DD': [{qtd, ts}, ...] }` — ao lado de
  `atosBalcao`, guarda cada lançamento individual (pra "desfazer último lançamento" e
  pra mostrar as pílulas com horário). Só incrementos **positivos** viram lançamento
  aqui; correções com -1 ou edição direta do total não entram nessa lista.
- **`p.pendencias`** (agenda de pendências/próximos passos, por protocolo): array de
  `{id, descricao, dataPrevista, responsavel, situacao: 'pendente'|'concluida'|
  'cancelada', notaConclusao, historico: [{situacao, ts, nota}], createdAt}`. Fica
  **separado** de `observacoesHistorico`/`historico` de status — nunca misturar os
  dados —, mas a criação e a conclusão de cada pendência também aparecem, só como
  leitura, na timeline unificada da ficha (ver `buildTimelineUnificada` abaixo);
  cancelamento e reabertura não entram lá, só na própria agenda. `computeAgendaBuckets()`
  é o único lugar que calcula os 4 grupos da faixa compacta (vencidas / hoje / próximos
  7 dias úteis / protocolos ativos sem nenhuma pendência pendente) — reaproveitar essa
  função em vez de recalcular em outro lugar.

## Regras de negócio que precisam ser respeitadas

- **Prazo fixo de 5 dias úteis** (`PRAZO_DIAS_UTEIS`), contado a partir da data de
  documentação completa, descontando fins de semana, feriados nacionais fixos,
  feriados móveis calculados (Páscoa → Carnaval, Sexta-feira Santa, Corpus Christi) e
  feriados extras cadastrados. **O usuário decidiu explicitamente não querer prazo
  diferente por tipo de ato** — não reabrir essa discussão sem ele pedir.
- **Arquivamento**: um protocolo é considerado arquivado quando o status é `isFinal` E
  (não exige digitalização OU `rascunhoDigitalizado === true`). Só a fase padrão
  "Finalizado" exige digitalização antes de arquivar; "Usuário desistiu" arquiva na
  hora. Fases finais novas que o usuário criar entram sem exigir digitalização, a
  menos que ele marque a caixa "Exige digitalização antes de arquivar".
- **Lixeira, não exclusão definitiva**: excluir um protocolo só marca `naLixeira=true`
  (com `dataExclusao`). Existe ação separada para excluir de vez. Nunca reverter isso
  para exclusão direta.
- **Vínculo entre protocolos** é manual (não por nome/CPF automático) — serve só para
  visualizar junto, não é um "processo" com identidade própria. A sugestão automática
  por nome do cliente é só um atalho pra facilitar o vínculo manual, nunca vincula
  sozinha. A função `applyVinculoManual(protocoloId, selectedIdsRaw)` (chamada pelo
  painel dedicado de vínculo) **duplica de propósito** a lógica de merge de
  `grupoVinculoId` que já existe dentro de `App.saveProtocolo`, em vez de extrair um
  helper compartilhado — no momento do merge dentro de `saveProtocolo` o payload ainda
  não está em `state.protocolos`, o que tornaria um helper único arriscado de mexer
  sem re-testar o fluxo de salvar já validado. Se for refatorar, testar os dois
  caminhos (criar/editar com vínculo E o painel dedicado) separadamente.
- **PF/PJ**: badge na ficha + filtro + opção de agrupar em seções — as três formas
  coexistem, nenhuma substitui a outra.
- **Responsável** é sempre um só por protocolo (seleção única), nunca múltiplo.
- **Observações** têm duas formas de histórico que coexistem: o histórico de mudança de
  status (automático, a cada troca) e o log de observações (o usuário escreve quando
  quiser, cada entrada fica datada e nenhuma apaga a anterior). As duas listas mostram
  a entrada mais recente primeiro.
- **Backup manual convive com a sincronização automática** — não é redundância a
  remover; é rede de segurança pra quando o artifact travar ou for despublicado
  (despublicar apaga os dados permanentemente e não dá pra publicar o mesmo artifact
  de novo).

## Padrões de UI já estabelecidos

- Estética "livro de protocolo/cartório": serifada (Source Serif 4) pros títulos,
  Inter no corpo, JetBrains Mono pra datas/números, paleta de papel, selos coloridos
  ("stamps") pros status.
- 4 modos de visualização em abas: Lista / Quadro (Kanban com arrastar-e-soltar) /
  Arquivados / Lixeira.
- **Animações são deliberadamente pontuais**, não incondicionais — existem flags
  "de um disparo só" (`justOpenedKey`, `justCreatedId`, `justSwitchedView`,
  `modalJustOpened`) que são setadas na ação do usuário e limpas logo depois do
  render, pra evitar que a animação replique em toda re-renderização não relacionada
  (isso já causou bugs de "piscar" a tela inteira a cada tecla digitada — ver
  armadilha abaixo).
- Enter salva observação; Shift+Enter quebra linha.
- Tipos de ato mais usados recentemente aparecem no topo da lista de seleção do
  formulário (não em Configurações, que mantém ordem original).
- **Confirmação de ações destrutivas**: duas abordagens coexistem por design, não por
  inconsistência. `window.confirm()` nativo continua em uso em pontos "de fora pra
  dentro" (ex.: `App.deleteProtocolo` mover-para-lixeira, `App.desvincularGrupo`).
  Já a Lixeira usa um cartão de confirmação inline (`.lx-confirm-card`, controlado por
  `confirmandoExclusaoId` — guarda o id do protocolo ou o literal `'__todos__'` pra
  "esvaziar tudo") porque excluir de vez é irreversível e merecia ficar visível no
  contexto, não num popup do navegador. Ao introduzir uma nova ação destrutiva,
  escolher conscientemente: se for reversível/já tem rede de segurança, `confirm()`
  nativo basta; se for definitivo, preferir o padrão de cartão inline.
- **Timeline unificada**: histórico de mudança de status, log de observações e
  criação/conclusão de pendências da agenda aparecem juntos numa única lista
  cronológica (mais recente primeiro), tanto no card da ficha na Lista quanto no
  painel de criar/editar. `buildTimelineUnificada(p)` é a única função que monta essa
  lista (mesclando os três, sem duplicar nada no `state`) — qualquer novo tipo de
  evento que deva aparecer aí entra como mais um `tipo` nesse array, com a
  renderização correspondente adicionada em `renderTimelineFicha` (ficha, com tag
  texto "status"/"obs"/"agenda") e `renderDiarioUnificado` (painel, com ponto colorido
  ou pílula). Isso é só uma visão de leitura — os dados de origem (`historico`,
  `observacoesHistorico`, `pendencias`) continuam cada um na sua estrutura própria.
- **Faixas compactas no topo da Lista**: agenda (`renderAgendaStrip`) e atos de balcão
  (`renderAtosBalcaoStrip`) — só aparecem na visão Lista, nunca em Quadro/Arquivados/
  Lixeira, pra não distrair durante outros fluxos. A faixa da agenda tem 4 números
  clicáveis (vencidas/hoje/próximos 7 dias úteis/sem próximo passo) que abrem um
  painel expansível com as linhas daquele grupo — clicar no número alterna
  aberto/fechado (`ui.agendaFiltroAberto`), clicar no nome do protocolo abre a ficha.

### Sistema visual (redesign `design_handoff_protocolos`)

Todas as 6 telas do app (Lista, Quadro/Kanban, Criar/Editar, Vínculo entre protocolos,
Atos de balcão, Lixeira) passaram por um redesign visual completo, feito em fases e
já 100% mesclado em `main`. A pasta `design_handoff_protocolos/` (README.md + o
protótipo `Protocolos - Lista e Quadro.dc.html`) é a fonte da linguagem visual — útil
como referência caso surjam dúvidas de intenção de design, mas o app já implementa
tudo que estava especificado lá.

- **Tokens CSS** (`:root`, topo do `<style>`): `--painel`, `--ficha`, `--apoio`,
  `--apoio-2`, `--barra-filtros`, `--tinta-media`, `--tinta-media-2`, `--apagado`,
  `--apagado-2`, `--carimbo`, `--borda`, `--borda-ficha`, `--borda-forte`,
  `--borda-atraso`, `--trilho`, `--divisor-suave`, `--r-card`, `--r-field`,
  `--r-chip`, `--r-selo`. Usar esses tokens (não cor hexadecimal solta) em qualquer
  CSS novo dentro dessas telas, pra manter consistência com o resto.
- **Container de painel lateral (`.side-overlay` + `.side-panel`)**: padrão
  compartilhado por Criar/Editar, painel de vínculo dedicado e o painel de Atos de
  balcão — desliza da direita, largura default 640px, com modificadores
  `.w-440`/`.w-520`/`.w-1000` pras variações de largura. **Configurações, Histórico do
  cliente e Relatório do dia continuam usando o `.overlay`/`.modal` antigo** (diálogo
  centralizado) — isso foi deliberado, pra limitar o raio de mudança do redesign;
  não converter essas três telas pro side-panel sem o usuário pedir.
  `.segmented`/`.seg-btn` (antigo) permanece só nos toggles internos PF/PJ e
  tipo-de-documento do formulário de criar/editar; o `.seg2`/`.seg2-btn` (novo) é
  exclusivo do controle Lista/Quadro/Arquivados/Lixeira na Lista — são famílias
  separadas de propósito, pra não colidir uma com a outra.
- **Famílias de classe por tela**: `.regua*` (régua de números/stats no topo),
  `.cp*` (cartão de ficha/protocolo na Lista, com modificador `.cp.lixeira`), `.selo`
  e `.tag-atraso` (selos de status/atraso), `.chip-status`, `.kb-*` (cartões e colunas
  do Kanban), `.fm-*` (campos do formulário de criar/editar — label, input, chip,
  dropdown, disclosure, etc.), `.grp-*`/`.pill-vinculo`/`.diarios-*`/`.diario-*`
  (agrupamento por vínculo e visão lado-a-lado), `.vp-*` (painel dedicado de vínculo),
  `.ab-*` (Atos de balcão — modal e faixa/strip), `.lx-*`/`.cp-lx-*`/`.btn-lx-*`
  (Lixeira). `.ib28` é um botão de ícone 28px reutilizado em várias telas.

## Armadilhas já encontradas (não reintroduzir)

1. **Campo de texto perdendo valor**: com a arquitetura de re-render total, se um campo
   só sincroniza seu valor "por tabela" (outro campo dispara `onchange` → recaptura
   tudo), digitar rápido em sequência entre campos pode causar uma corrida onde o
   valor digitado é perdido bem no meio da troca de foco. A correção foi: todo campo
   de texto do formulário tem seu próprio `oninput="App.setField('nome', this.value)"`
   que atualiza o rascunho (`draftModal`) imediatamente, **sem** disparar
   re-renderização. Seguir esse padrão em campos novos.
2. **Editar um protocolo apagando campos que a tela de edição não mostra**: o
   `payload` montado em `App.saveProtocolo` precisa **sempre** herdar do registro
   original (`original.campo`) qualquer campo que não seja editável naquele
   formulário (ex.: `rascunhoDigitalizado`, `dataDigitalizacao`) — já aconteceu de um
   `payload` novo sobrescrever o protocolo inteiro e resetar esses campos.
3. **Animação incondicional em elemento que renderiza toda hora**: nunca colocar
   `animation:` direto numa classe CSS de algo que é recriado em toda renderização
   (fichas, cabeçalhos de grupo, cartões do kanban). Usar as flags de "um disparo só"
   citadas acima.
4. **Falso positivo no dirty-check do painel de criar/editar** (`draftModalSnapshot` /
   `isDraftDirty()`, usado pra confirmar antes de fechar com Esc/clique fora): se o
   snapshot for tirado logo depois de montar `draftModal`, sem passar pela captura dos
   campos de texto, valores padrão "fantasma" (ex.: data de hoje) só entram no
   `draftModal` na primeira chamada de `captureModalTextFields()` — daí um Esc
   imediato, sem nenhuma mudança real, aparentava "alterações não salvas". Corrigido
   ao garantir a ordem `App.render()` → `captureModalTextFields()` → só então tirar o
   snapshot (ver `App.openNew`/`App.openEdit`). Qualquer novo fluxo que abra o painel
   precisa seguir essa mesma ordem.
5. **Mesmo falso positivo ao expandir campos opcionais**: em `App.toggleCamposOpcionais`
   (abertura rápida), revelar campos com valor padrão (nº/data do protocolo) disparava
   o mesmo problema do item 4. Corrigido medindo `isDraftDirty()` **antes** de
   expandir; depois de expandir+renderizar+capturar, só atualiza o snapshot se ainda
   não estava sujo antes (preserva alteração real do usuário, absorve só o ruído dos
   defaults recém-revelados).

## Fluxo de trabalho até aqui

O projeto começou publicado como artifact do Claude.ai, testado com Playwright antes
de cada entrega. O usuário teve problemas recorrentes com o artifact publicado não
puxar atualizações novas automaticamente (causa nunca confirmada) — por isso migrou
pro Claude Code com repositório próprio no GitHub (`fabricio-lv/controle-atos-cartorio`),
app servido pelo GitHub Pages, buscando um fluxo mais confiável baseado em git/PR.

- **Ciclo de trabalho padrão**: `git checkout -b feat/xxx` → implementar/testar →
  commit (mensagem detalhada em português, terminando com
  `Co-Authored-By: Claude <modelo> <noreply@anthropic.com>`) → `git push -u origin
  feat/xxx` → o usuário revisa/pede o PR e responde "mescla e continua" → checar se o
  GitHub já mesclou (`git fetch origin`); se não, `git checkout main && git merge
  --ff-only origin/feat/xxx && git push origin main` → faxina: apagar a branch local e
  remota e confirmar que só `main` restou. Se um `git push` inesperadamente reportar
  non-fast-forward, é sinal de que o GitHub já tem um merge commit que o repo local
  não tem ainda — resolver com `git merge --ff-only origin/main` (nunca force-push).
- **Teste manual/automatizado**: sem Node/Python/PHP disponíveis nesta máquina, o
  servidor de desenvolvimento é um script PowerShell puro (`.claude/serve.ps1`,
  configurado em `.claude/launch.json`, porta 8123). Testes de UI usam as ferramentas
  de browser (`preview_start` → `navigate` → `javascript_exec`/`computer` →
  `read_console_messages`) em vez de Playwright.
