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
- **Re-render total a cada mudança de estado**: `App.render()` chama `renderAll()`, que
  reconstrói `#app.innerHTML` inteiro. Isso já causou bugs sutis (ver seção "Armadilhas"
  abaixo) — qualquer novo campo de texto/interação precisa levar isso em conta.
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
  correspondente em `migrate()`.

## Modelo de dados (`state`)

- **`protocolos`**: array de atos. Campos principais: `id`, `numeroProtocolo`,
  `cliente`, `clienteTelefone`, `clienteEmail`, `outorgados`, `responsavel`,
  `tipoPessoa` (`pf`/`pj`), `canais` (array — um protocolo pode ter vários canais de
  atendimento), `dataProtocolo`, `docsCompletos`, `dataRecebimentoCompleto`, `status`,
  `tipos` (array de tipos de ato), `observacoesHistorico` (array `{texto, ts}`),
  `historico` (array `{status, ts}` — toda mudança de status fica registrada com
  data/hora), `rascunhoDigitalizado`, `dataDigitalizacao`, `grupoVinculoId` (vínculo
  manual com outros protocolos), `naLixeira`, `dataExclusao`, `createdAt`.
- **`tiposAtos`**: lista de tipos de procuração/escritura, editável em Configurações.
- **`statusList`**: fases de andamento, **totalmente configuráveis pelo usuário**
  (adicionar, editar, reordenar, remover). Cada fase tem `{key, label, cor, isFinal,
  requerDigitalizacao}`. `cor` é uma das chaves de `PALETTE` (gray/gold/blue/plum/
  green/dark/teal/rose) e corresponde a variáveis CSS com o mesmo nome.
- **`responsaveis`**: lista de nomes pré-definidos (editável), usada como `<select>` no
  formulário — não é texto livre. `ultimoResponsavel` guarda o último usado, que vira
  padrão ao abrir "+ Novo Protocolo".
- **`feriadosExtras`** / **`feriadosMoveis`**: configuração de feriados para o cálculo
  de prazo.
- **`atosBalcao`**: `{ 'YYYY-MM-DD': quantidade }` — contador simples de atos que não
  geram protocolo (atendimento só de balcão). Completamente separado dos protocolos.
- **`documentosChecklist`** / `documentosMarcados` (por protocolo): **campo já existe no
  modelo de dados e na migração, mas a UI nunca foi construída** — é uma ideia
  (checklist de documentos específicos por tipo de ato, tipo "RG, CPF, comprovante de
  residência") que ficou só esboçada. Se for retomar, é o próximo passo natural.

## Regras de negócio que precisam ser respeitadas

- **Prazo fixo de 5 dias úteis** (`PRAZO_DIAS_UTEIS`), contado a partir da data de
  documentação completa, descontando fins de semana, feriados nacionais fixos,
  feriados móveis calculados (Páscoa → Carnaval, Sexta-feira Santa, Corpus Christi) e
  feriados extras cadastrados. **O usuário decidiu explicitamente não querer prazo
  diferente por tipo de ato** — não reabrir essa discussão sem ele pedir.
- **Arquivamento**: um protocolo é considerado arquivado quando o status é `isFinal` E
  (não exige digitalização OU `rascunhoDigitalizado === true`). Só a fase padrão
  "Finalizado" exige digitalização antes de arquivar; "Cliente desistiu" arquiva na
  hora. Fases finais novas que o usuário criar entram sem exigir digitalização, a
  menos que ele marque a caixa "Exige digitalização antes de arquivar".
- **Lixeira, não exclusão definitiva**: excluir um protocolo só marca `naLixeira=true`
  (com `dataExclusao`). Existe ação separada para excluir de vez. Nunca reverter isso
  para exclusão direta.
- **Vínculo entre protocolos** é manual (não por nome/CPF automático) — serve só para
  visualizar junto, não é um "processo" com identidade própria. A sugestão automática
  por nome do cliente é só um atalho pra facilitar o vínculo manual, nunca vincula
  sozinha.
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

## Fluxo de trabalho até aqui

Todo o desenvolvimento foi feito por chat, com o Claude gerando o HTML inteiro,
testando com Playwright (headless) antes de cada entrega, e publicando como artifact
do Claude.ai. O usuário teve problemas recorrentes com o artifact publicado não
puxar atualizações novas automaticamente (causa nunca confirmada — pode ser
infraestrutura do Claude.ai) — por isso a migração para o Claude Code com repositório
próprio no GitHub, buscando um fluxo mais confiável baseado em git/PR.
