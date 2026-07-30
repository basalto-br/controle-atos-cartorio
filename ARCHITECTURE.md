# Arquitetura — controle-atos.html

Aplicativo de página única (HTML + CSS + JS puro, sem framework/build/bundler) para controle
de protocolos de atos notariais (procurações e escrituras) num cartório de notas. Todo o CSS
fica num único bloco `<style>` inline e todo o JS roda dentro de uma IIFE `(function(){...})()`
num único bloco `<script>` inline. Não há DOM persistente por componente: cada ação do usuário
muda variáveis de estado em memória e chama `App.render()`, que reconstrói `#app.innerHTML`
inteiro a partir de funções `renderX()` que retornam strings HTML; os elementos interativos
disparam ações via `onclick="App.xxx(...)"` inline apontando para métodos do objeto global `App`.

> Nota: linhas revisadas e reconferidas em 30/07/2026 após a adição da feature "Tarefas" (lista
> de a-fazer independente da entidade `protocolos`, com checklist fixo de 3 etapas para
> retificação/averbação/aditamento e para substabelecimento/revogação/renúncia, ou modo livre
> pendente/concluída). O CSS (bloco `<style>`, linhas 7–693) não foi tocado — a UI de Tarefas
> reaproveita classes já existentes (`.side-overlay`, `.side-panel`, `.hist-toggle`, `.hist-box`,
> `.hist-row`, `.fm-label`, `.fm-input`, `.fm-sec-head`, `.fm-seg-pessoa`), confirmado por Grep
> sem nenhuma classe nova. O arquivo tem 5055 linhas nesta revisão (antes da feature: 4638).

## Mapa de estrutura

| Section | Start line | End line | Description |
|---|---|---|---|
| Doctype / head / meta | 1 | 6 | `<!DOCTYPE>`, `<html lang="pt-BR">`, charset, viewport, `<title>` |
| Abertura do `<style>` | 7 | 8 | Tag `<style>` + comentário explicando que as fontes embutidas eliminam requisições de rede (offline/LGPD) |
| Fontes embutidas (base64 `@font-face`) | 9 | 16 | 8 declarações `@font-face` com Source Serif 4, Inter e JetBrains Mono embutidas em base64, uma por linha |
| Tokens de design CSS (`:root`) | 18 | 62 | Variáveis CSS: cores base, superfícies (`--painel`/`--ficha`/`--apoio`), bordas, pares cor/cor-suave por status, raios (`--r-card` etc.), famílias de fonte |
| Reset global / body / `#app` | 63 | 73 | `box-sizing` global, tipografia do `body`, container `#app` |
| CSS — Header e botões | 74 | 141 | Letterhead, regra do cabeçalho, banners (warning/ok/info/link), linha "hoje", variantes de `.btn` (primary/ghost/danger), mini/icon buttons |
| CSS — Stats e barra de filtros | 142 | 210 | `.stats-bar`/`.stat`, `.filters-bar`, busca, `.segmented`/`.seg2` (Lista/Quadro/Arquivados/Lixeira) |
| CSS — Componentes de disclosure e selos compartilhados | 211 | 251 | `.empty-state` (+ `.big`), `.group-header` (+ `:first-child`/`.cnt`), `.tag` (chips do picker de vínculo), `.docs-pending` (usado por `renderGateDigitalizacao`), `.stamp` (+ variantes de cor, usado em `renderVinculados`), `.hist-toggle`/`.hist-box`/`.hist-row` (disclosure reaproveitado em histórico, checklist, agenda, vínculo, modal de histórico do usuário, Configurações **e agora também no checklist de Tarefas**), `.kanban-hint` (usado em `renderFiltersBar`) |
| CSS — Animações e campos de formulário legado | 253 | 281 | Keyframes (fadeIn/fadeSlideIn/highlightNew), `.anim-in`/`.ficha-new`, estilos legados de `.field`/`.checklist`/`.add-tipo-row` |
| CSS — Painel lateral (`.side-*`) e formulário por seções (`.fm-*`) | 282 | 408 | `.side-panel`/`.side-overlay` (painel único usado por criar/editar, Configurações, Histórico, Relatório do dia, Atos de balcão **e Tarefas**); formulário numerado por seções (`.fm-sec*`, `.fm-row`, `.fm-field`, `.fm-label`, `.fm-input*`, `.fm-warn`, `.fm-seg-pessoa`, `.fm-chip`, `.fm-dropdown`, `.fm-prazo-box`, `.fm-disclosure*`); CSS de Configurações (`.settings-section`, `.status-row`, `.swatch`) e do relatório do dia (`.report-*`); inclui dois `@media` embutidos (760px: `edit-grid` vira 1 coluna; 600px: empilha `letterhead`/`stats`/`field-row`) |
| CSS — Redesign Fase 1: Ficha (`.cp-*`) e Quadro (`.kb-*`) | 410 | 497 | Sistema visual atual: régua de números, cartão de ficha (`.cp`, `.cp-prazo`, `.trilha`), colunas e cartões do kanban (`.kb-board`, `.kb-card`, dropzone de drag-and-drop) |
| CSS — Vínculo entre protocolos | 498 | 549 | Pílula de vínculo, cabeçalho/lista de grupo vinculado, estilos do painel de vínculo |
| CSS — Atos de balcão e faixas de agenda | 550 | 621 | Painel e faixa de atos de balcão (`.ab-*`), barras por dia/mês, chips e painel expandido da agenda (`.agenda-row-*`) |
| CSS — Lixeira e responsivo da ficha | 622 | 648 | Cartão da lixeira, botões restaurar/excluir, card de confirmação de exclusão, `@media (max-width:700px)` da grade da ficha |
| CSS — Diversos (stats clicáveis, busca, toasts, área de impressão da ficha) | 650 | 684 | `.stat.clickable`/`.banner-alert`, botão de limpar busca, `#toast-layer`, marcação oculta `#fichaPrintArea` usada só na impressão |
| CSS — `@media print` | 685 | 692 | Regras de impressão: esconde tudo exceto `#dailyReportPrint` ou, em modo ficha, `#fichaPrintArea` |
| Fechamento do `<style>` + esqueleto do `<body>` | 693 | 699 | `</style>`, `<body>` com apenas `#app` (placeholder "Carregando…"), `#toast-layer` e `#fichaPrintArea` — todo o resto do DOM é gerado pelo JS |
| Abertura do `<script>`/IIFE + constantes gerais | 700 | 753 | `"use strict"`; `PALETTE`, `DEFAULT_STATUS_LIST` (8 fases padrão), `CANAIS`, `DEFAULT_TIPOS`, `DEFAULT_DOCUMENTOS_CHECKLIST` |
| Categorização automática de tipo de ato | 755 | 786 | `CATEGORIAS_ATO`, `categoriaOposta`, `normalizarSemAcento`, `categorizarTipoPorNome` (heurística por prefixo, sem acento), `getCategoriaDoTipo` |
| Checklist de documentos (dados base) | 788 | 809 | `DOCUMENTOS_BASE_CHECKLIST` (fixa, não editável) e `getChecklistDoProtocolo(p)`, que soma base + `checklistPorTipo` + `documentosExtras` do protocolo |
| Constantes de persistência + variáveis globais de estado/UI | 811 | 886 | `PRAZO_DIAS_UTEIS`, chaves de storage/IndexedDB/backup, variáveis globais `state`, `ui`, flags de modal/painel abertos (inclui as novas `tarefasModalOpen`, `tarefaDraft`, `tarefaBuscaProtocolo`, `tarefaConfirmandoExclusaoId`, `tarefasConcluidasAbertas`), `ETIQUETAS_OBS`, helpers `getEtiquetaObs`/`chaveDispensaVinculo` |
| Tarefas — helpers puros (`defaultTarefaEtapas` / `recomputeTarefaStatus`) | 888 | 930 | `defaultTarefaEtapas(tipo, origemAto)` monta o checklist fixo de 3 etapas (etapa 3 varia entre "Anotar no livro" e "Comunicar Cartório de origem" conforme tipo/origem); `recomputeTarefaStatus(t)` deriva `etapa3.feita` das 2 subetapas e recalcula `status`/`concluidoEm` — no-op para tarefas tipo `'livre'` |
| Estado padrão (`defaultState`) + `inserirFaseAposChave` | 932 | 962 | Schema default do `state` (`protocolos`, **`tarefas: []`**, `tiposAtos`, `statusList`, `responsaveis`, `atosBalcao`, `sugestoesDispensadas`, `categoriaPorTipo`, `checklistPorTipo` etc.) + `inserirFaseAposChave` (helper idempotente para acrescentar fases novas em instalações existentes) |
| `migrate(raw)` | 964 | 1088 | Roda em todo carregamento: preenche campos ausentes de `protocolos`/`state`, insere fases novas do `statusList`, normaliza contato legado, calcula `rascunhoDigitalizado` retroativo, **e agora também faz o backfill de `state.tarefas`** (normaliza `tipo`/`origemAto`/`etapas` de dados legados ou incompletos, reconciliando por `key` com o template de `defaultTarefaEtapas` e chamando `recomputeTarefaStatus`) |
| Persistência: storage/File System Access/backups | 1090 | 1283 | `ensureStorage` (fallback de `window.storage`), `loadState`/`saveState`, cache do handle no IndexedDB, `fsVerifyPermission`/`fsQueryGranted`, `loadFromDir`, `fsFlush` (grava na pasta conectada), `writeBackupSnapshot`/`pruneBackups`, `checkScheduledBackups` (10:50 e 17:45) |
| Cálculo de prazo, dias úteis e agenda | 1284 | 1441 | Utilidades de data, feriados móveis (Páscoa), `isBusinessDay`/`addBusinessDays`/`businessDaysBetween`, `getStatusMap`, `isArquivado`, `needsDigitalizacaoGate`, `getVinculados`, `pendenciasPendentes`, `computeAgendaBuckets`, `computePrazo` (cálculo de prazo de 5 dias úteis) |
| Helpers diversos | 1442 | 1520 | `esc`/`jsAttr` (escape HTML), `uid`, `applyVinculoManual` (merge de grupo de vínculo manual), `removeAccents`/`slugify`, `withFocus` (preserva foco/seleção/scroll ao re-renderizar) |
| `App` — ações principais (filtros, protocolo, documentos, pendências) | 1522 | 2373 | Início do objeto `App` (`App.render`, `App.showToast`); handlers de busca/filtros/ordenação/visão; toggles de timeline/vínculo/documentos; `App.openNew`/`openEdit`/`saveProtocolo`/`deleteProtocolo`; lixeira; `avancarFase`/`changeStatusQuick`; observações e pendências da ficha; inclui helpers puros embutidos `matchesFilters`, `sortComparator`, `getFilteredSorted` |
| `App` — drag-and-drop do Kanban | 2374 | 2399 | `App.dragStart`/`markAlvo`/`limpaDrag`/`dragEnd`/`dropOnColumn` |
| `App` — histórico do usuário, relatório do dia, impressão | 2400 | 2461 | `App.showClienteHistory`, `openDailyReport`/`closeDailyReport`/`printDailyReport`, `buildFichaPrintHTML`, `printFicha` |
| `App` — ações de atos de balcão | 2462 | 2515 | `App.openAtosBalcao`, `ajustarAtoBalcao`, `adicionarQuantidadeBalcao`, `desfazerUltimoLancamentoBalcao`, edição do total do dia |
| `App` — exportação CSV de atos de balcão | 2516 | 2532 | `App.exportAtosBalcaoCSV` |
| `App` — Tarefas (a fazer) | 2534 | 2683 | `App.openTarefas`, `closeTarefas`, `setTarefaDraftTipo`, `setTarefaDraftOrigemAto`, `setTarefaDraftField`, `setTarefaBuscaProtocolo`, `selecionarProtocoloTarefa`, `limparProtocoloTarefa`, `addTarefa`, `toggleEtapaTarefa`, `toggleSubetapaTarefa`, `reabrirTarefa`, `setNumeroLivroTarefa`, `setFolhaTarefa`, `toggleTarefaLivreStatus`, `toggleTarefasConcluidas`, `pedirExcluirTarefa`, `cancelarExcluirTarefa`, `deleteTarefa` — CRUD e transições de status da lista de tarefas, independente de `protocolos` |
| `App` — exportação CSV de protocolos | 2684 | 2729 | `App.exportCSV` (gera CSV com todos os campos visíveis da lista filtrada) |
| `App` — backup manual (export/import JSON) | 2730 | 2777 | `App.exportBackup`/`triggerImportBackup`/`importBackupFile` — rede de segurança independente da pasta conectada, sempre substitui o `state` via `migrate()` |
| `App` — pasta de dados e Configurações | 2778 | 3009 | `App.conectarPastaDados`/`reconectarPasta`/`desconectarPasta`; `openSettings`/`closeSettings`; CRUD de tipos de ato, checklist por tipo, responsáveis, fases do `statusList` e feriados extras/móveis nas Configurações |
| Render — banner de storage + render mestre + header/stats/filtros | 3010 | 3178 | `renderFsBanner`, `renderAll` (monta e injeta `#app.innerHTML` inteiro, incluindo `tarefasModalOpen ? renderTarefasModal() : ''`), `renderHeader` (agora com o botão "Tarefas (N)" e badge de pendentes, logo após o botão "Atos de balcão"), `renderStats`, `renderFiltersBar` |
| Render — timeline unificada e peças da ficha (documentos, pendências, lixeira) | 3179 | 3485 | `buildTimelineUnificada` (junta histórico de status + observações + pendências numa timeline só de leitura, sem duplicar dados de origem), `renderTipoTagTimeline`, `renderTimelineFicha`, `renderGateDigitalizacao` (gate de digitalização — usa `.docs-pending`), `renderVinculados`, `renderDocumentosChecklist`, `renderPendenciasFicha`, `renderLixeiraItem`, `renderConfirmExclusaoCard`, `renderTrilha`, `renderColunaPrazo` |
| Render — ficha completa e grupos vinculados | 3486 | 3597 | `renderFicha`, `renderGrupoVinculado`, `renderListaComVinculo` |
| Render — diários lado a lado e painel de vínculo | 3598 | 3745 | `renderDiariosLadoALado`, `renderLinhaVinculoPanel`, `renderPainelVinculo` |
| Render — área de lista/quadro e Kanban | 3747 | 3822 | `renderListArea` (alterna Lista/Quadro/Arquivados/Lixeira), `renderKanbanCard`, `renderKanban` |
| Render — painel de criar/editar protocolo | 3824 | 4291 | `renderModalQuickBody`, `renderPrazoLeituraHtml`, `renderEtiquetaChipsPicker`, `renderPilulaEtiqueta`, `renderDiarioUnificado`, `renderModal` (maior função de render do app — painel lateral completo de criar/editar) |
| Render — modal de Configurações | 4293 | 4489 | `renderSettingsModal` |
| Render — modal de histórico do usuário | 4490 | 4526 | `renderClienteHistoryModal` |
| Render — modal de relatório do dia | 4527 | 4593 | `renderDailyReportModal` |
| Render — modal de atos de balcão | 4595 | 4718 | `computeSemanaBalcao`/`computeMesBalcaoPorSemana` (agregações para os gráficos), `renderAtosBalcaoModal` |
| Render — modal de Tarefas (a fazer) | 4719 | 4894 | `computeBuscaProtocoloTarefa`, `renderTarefaChecklist`, `renderConfirmExclusaoTarefaCard`, `renderTarefaLinha`, `renderTarefasModal` — painel lateral no mesmo estilo do de Atos de Balcão |
| Render — faixas de agenda e atos de balcão | 4896 | 4977 | `renderAgendaStrip`, `renderAgendaPainel`, `renderAtosBalcaoStrip`, `renderFaixasSecundarias` |
| Bootstrap / inicialização | 4978 | 5024 | `fallbackLoad` (usa `window.storage`), `bootstrap()` (tenta reconectar a pasta via File System Access; cai no fallback em cada etapa que falhar) |
| Atalhos de teclado + chamadas de boot + fechamento | 5026 | 5055 | Listener de `keydown` (N = novo, `/` = busca, Esc = fecha modal/painel/busca), chamadas `ensureStorage()`/`bootstrap()`, `setInterval(checkScheduledBackups, 60000)`, fechamento da IIFE, `</script></body></html>` |
