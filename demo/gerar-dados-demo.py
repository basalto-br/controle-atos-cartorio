#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera dados-demo.json — um backup completo do Controle de Atos, com protocolos
ficticios, para apresentar a ferramenta sem abrir producao vazia.

    python demo/gerar-dados-demo.py

Por que gerador e nao um arquivo fixo: as datas sao relativas ao dia em que roda.
Um arquivo congelado envelhece — em duas semanas o "no prazo" vira "atrasado" e a
demonstracao passa a mostrar um cartorio em colapso. Rode de novo antes da conversa.

O formato de saida e exatamente o que App.exportBackup grava: o objeto `state`
inteiro. Ele entra pelo mesmo caminho de importacao de backup e passa por
migrate(), entao os campos que faltarem aqui sao preenchidos la.

NENHUM dado real. Nomes, documentos, telefones e a serventia sao inventados.
"""

import json
import os
from datetime import date, timedelta

# ---------------------------------------------------------------- dias uteis
# Espelha isBusinessDay/addBusinessDays do controle-atos.html. Se o calendario
# de feriados mudar la, mude aqui — o prazo de 5 dias uteis depende dos dois
# concordarem, e um desencontro so aparece como data estranha na tela.

def pascoa(ano):
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def feriados(ano):
    s = {
        date(ano, 1, 1), date(ano, 4, 21), date(ano, 5, 1),
        date(ano, 9, 7), date(ano, 10, 12), date(ano, 11, 2),
        date(ano, 11, 15), date(ano, 12, 25),
    }
    if ano >= 2024:
        s.add(date(ano, 11, 20))
    p = pascoa(ano)
    s.add(p - timedelta(days=2))    # sexta-feira santa
    s.add(p - timedelta(days=47))   # carnaval
    s.add(p + timedelta(days=60))   # corpus christi
    return s


def dia_util(d):
    return d.weekday() < 5 and d not in feriados(d.year)


def mais_dias_uteis(d, n):
    while n > 0:
        d += timedelta(days=1)
        if dia_util(d):
            n -= 1
    return d


def menos_dias_uteis(d, n):
    while n > 0:
        d -= timedelta(days=1)
        if dia_util(d):
            n -= 1
    return d


def desloca(d, n):
    """n dias uteis a frente (positivo) ou atras (negativo). 0 = hoje, ou o
    proximo dia util se hoje cair em fim de semana ou feriado."""
    if n > 0:
        return mais_dias_uteis(d, n)
    if n < 0:
        return menos_dias_uteis(d, -n)
    return d if dia_util(d) else mais_dias_uteis(d, 1)


_HOJE_REAL = date.today()
# Ancora da demonstracao. Se cair em sabado, domingo ou feriado, tudo e montado
# para o proximo dia util: cartorio nao abre no fim de semana, e sem isso o
# protocolo que deveria "vencer hoje" apareceria vencendo so na segunda — e os
# deslocamentos de 0 e de 1 dia util colapsariam na mesma data.
HOJE = _HOJE_REAL if dia_util(_HOJE_REAL) else mais_dias_uteis(_HOJE_REAL, 1)

PRAZO_DIAS_UTEIS = 5
ONUS_VALIDADE_DIAS = 30


def iso(d):
    return d.isoformat()


def ts(d, hora=10, minuto=30):
    """Epoch em milissegundos, como Date.now() no app."""
    from datetime import datetime
    return int(datetime(d.year, d.month, d.day, hora, minuto).timestamp() * 1000)


def recebimento_para_vencer_em(n):
    """Data de documentacao completa que faz o prazo vencer em n dias uteis
    a partir de hoje. n negativo = ja venceu ha n dias uteis."""
    return menos_dias_uteis(desloca(HOJE, n), PRAZO_DIAS_UTEIS)


def onus_emitida_para_vencer_em(dias_corridos):
    """Data de emissao da certidao que faz a validade de 30 dias corridos
    terminar daqui a `dias_corridos`. Negativo = ja vencida."""
    return HOJE + timedelta(days=dias_corridos) - timedelta(days=ONUS_VALIDADE_DIAS)


# ------------------------------------------------------------------ pessoas
# Inventados de proposito. Nao usar nome de pessoa ou serventia real aqui,
# nem em captura de tela: o repositorio e publico.

RESPONSAVEIS = ["Marina Salles", "Tiago Mendonça", "Rafaela Bittencourt"]

TIPOS = [
    "Procuração Ad Judicia",
    "Procuração Ad Negotia",
    "Procuração para venda de imóvel",
    "Procuração bancária/financeira",
    "Escritura de Compra e Venda",
    "Escritura de Doação",
    "Escritura de Inventário e Partilha",
    "Escritura de União Estável",
    "Escritura de Divórcio Consensual",
    "Escritura Declaratória",
]

DOCS_BASE = [
    "Documento de identificação com CPF do(s) outorgante(s)",
    "Documento de identificação com CPF do(s) outorgado(s)",
    "Qualificação do(s) outorgante(s)",
    "Qualificação do(s) outorgado(s)",
]

CHECKLIST_POR_TIPO = {
    "Procuração para venda de imóvel": [
        "Matrícula atualizada do imóvel",
        "Certidão de ônus reais",
        "IPTU do exercício",
    ],
    "Escritura de Compra e Venda": [
        "Matrícula atualizada do imóvel",
        "Certidão negativa de débitos municipais",
        "Comprovante de pagamento do ITBI",
        "Certidão de ônus reais",
    ],
    "Escritura de Inventário e Partilha": [
        "Certidão de óbito",
        "Certidão negativa de testamento (CENSEC)",
        "Plano de partilha assinado pelos herdeiros",
        "Certidão negativa de débitos federais",
    ],
    "Escritura de Divórcio Consensual": [
        "Certidão de casamento atualizada",
        "Acordo de partilha de bens",
    ],
}

# --------------------------------------------------------------- protocolos
# Cada entrada foi escolhida para mostrar UM comportamento da ferramenta.
# A coluna "mostra" existe para quem for editar isto depois nao apagar sem
# querer o unico protocolo que exercita alguma regra.

protocolos = []
GRUPO_VINCULO = "gdemovenda01"


def add(
    n, numero, cliente, tipos, status, responsavel,
    mostra,                      # so documentacao, nao vai para o JSON
    tipo_pessoa="pf",
    dias_prazo=None,             # vencimento em dias uteis a partir de hoje
    docs_completos=True,
    protocolo_ha=None,           # dias corridos atras em que foi protocolado
    canais=None,
    outorgados="",
    telefone="",
    email="",
    documento="",
    onus_dias=None,              # dias corridos ate a certidao vencer
    onus_sem_data=False,
    digitalizado=False,
    observacoes=None,
    pendencias=None,
    marcados=None,
    grupo=None,
    na_lixeira=False,
    excluido_ha=None,
    valor=None,
):
    pid = "pdemo%02d" % n
    d_protocolo = HOJE - timedelta(days=protocolo_ha if protocolo_ha is not None else 6)
    d_receb = recebimento_para_vencer_em(dias_prazo) if (docs_completos and dias_prazo is not None) else None

    historico = [{"status": "aguardando_documentos", "ts": ts(d_protocolo, 9, 15)}]
    if status != "aguardando_documentos":
        base = d_receb or (d_protocolo + timedelta(days=1))
        historico.append({"status": status, "ts": ts(base, 14, 5)})

    obs = []
    for texto, dias_atras, etiqueta in (observacoes or []):
        obs.append({
            "texto": texto,
            "ts": ts(HOJE - timedelta(days=dias_atras), 11, 20),
            "etiqueta": etiqueta,
            "editadoEm": None,
        })

    pend = []
    for i, (desc, prev_dias, resp, situacao) in enumerate(pendencias or []):
        d_prev = desloca(HOJE, prev_dias)
        criada = HOJE - timedelta(days=3)
        item = {
            "id": "%s-pend%d" % (pid, i + 1),
            "descricao": desc,
            "dataPrevista": iso(d_prev),
            "responsavel": resp,
            "situacao": situacao,
            "notaConclusao": None,
            "historico": [{"situacao": "pendente", "ts": ts(criada, 9, 40), "nota": None}],
            "createdAt": ts(criada, 9, 40),
        }
        if situacao == "concluida":
            item["notaConclusao"] = "Recebido pelo balcão e conferido."
            item["historico"].append({
                "situacao": "concluida",
                "ts": ts(HOJE - timedelta(days=1), 16, 10),
                "nota": item["notaConclusao"],
            })
        pend.append(item)

    protocolos.append({
        "id": pid,
        "numeroProtocolo": numero,
        "cliente": cliente,
        "clienteTelefone": telefone,
        "clienteEmail": email,
        "clienteDocumento": documento,
        "outorgados": outorgados,
        "responsavel": responsavel,
        "tipoPessoa": tipo_pessoa,
        "canais": canais or ["balcao"],
        "dataProtocolo": iso(d_protocolo),
        "docsCompletos": docs_completos,
        "dataRecebimentoCompleto": iso(d_receb) if d_receb else None,
        "dataOnus": "" if (onus_sem_data or onus_dias is None) else iso(onus_emitida_para_vencer_em(onus_dias)),
        "valorAto": valor,
        "status": status,
        "tipos": tipos,
        "observacoesHistorico": obs,
        "historico": historico,
        "rascunhoDigitalizado": digitalizado,
        "dataDigitalizacao": iso(HOJE - timedelta(days=2)) if digitalizado else None,
        "grupoVinculoId": grupo,
        "documentosMarcados": marcados or {},
        "documentosExtras": [],
        "pendencias": pend,
        "naLixeira": na_lixeira,
        "dataExclusao": iso(HOJE - timedelta(days=excluido_ha)) if excluido_ha else None,
        "createdAt": ts(d_protocolo, 9, 15),
    })


add(1, "2026-0834", "Helena Vasconcelos Prado",
    ["Procuração Ad Judicia"], "aguardando_documentos", "Marina Salles",
    mostra="documentacao incompleta — prazo ainda nao comecou a contar",
    docs_completos=False, protocolo_ha=2, canais=["balcao"],
    outorgados="Dr. Anselmo Ribeiro Tavares",
    telefone="(27) 99000-0001",
    marcados={DOCS_BASE[0]: True},
    observacoes=[("Faltou a qualificação do outorgado. Avisado no balcão.", 2, None)])

add(2, "2026-0836", "Otávio Camargo Lins",
    ["Escritura de Doação"], "pendencia_documentos", "Tiago Mendonça",
    mostra="fase que depende do usuario — relogio corre, mas nao acusa atraso",
    dias_prazo=-3, protocolo_ha=12, canais=["whatsapp", "balcao"],
    telefone="(27) 99000-0002",
    email="otavio.lins@exemplo.com.br",
    observacoes=[("Aguardando o doador trazer a certidão de casamento atualizada.", 4, "pendencia")],
    pendencias=[("Cobrar certidão de casamento", 1, "Tiago Mendonça", "pendente")])

add(3, "2026-0841", "Beatriz Nogueira Sampaio",
    ["Procuração Ad Negotia"], "em_confeccao", "Marina Salles",
    mostra="vence HOJE",
    dias_prazo=0, protocolo_ha=9,
    telefone="(27) 99000-0003",
    outorgados="Clarice Nogueira Sampaio",
    marcados={d: True for d in DOCS_BASE})

add(4, "2026-0843", "Transportadora Vale Norte Ltda.",
    ["Procuração bancária/financeira"], "em_confeccao", "Rafaela Bittencourt",
    mostra="ATRASADO — o unico vermelho de verdade da lista + pendencia VENCIDA",
    tipo_pessoa="pj", dias_prazo=-2, protocolo_ha=11,
    canais=["email"],
    email="administrativo@valenorte.exemplo.com.br",
    documento="00.000.000/0001-00",
    outorgados="Sérgio Amorim Peçanha",
    marcados={d: True for d in DOCS_BASE},
    observacoes=[("Procuração precisa sair hoje — cliente cobrou por e-mail.", 1, "urgente")],
    pendencias=[("Confirmar os poderes com o setor jurídico da empresa", -2,
                 "Rafaela Bittencourt", "pendente")])

add(5, "2026-0845", "Joana Ferraz Coutinho",
    ["Escritura de Inventário e Partilha"], "em_analise", "Tiago Mendonça",
    mostra="no prazo, com checklist longo pela metade",
    dias_prazo=2, protocolo_ha=8,
    telefone="(27) 99000-0005",
    valor=480000.0,
    marcados={
        DOCS_BASE[0]: True, DOCS_BASE[2]: True,
        "Certidão de óbito": True,
        "Certidão negativa de testamento (CENSEC)": True,
    },
    pendencias=[("Pedir certidão negativa de débitos federais", 2, "Tiago Mendonça", "pendente"),
                ("Conferir plano de partilha com os herdeiros", -1, "Rafaela Bittencourt", "concluida")])

add(6, "2026-0847", "Ricardo Malheiros Fontes",
    ["Escritura de União Estável"], "em_conferencia_usuario", "Rafaela Bittencourt",
    mostra="minuta com o usuario para conferencia",
    dias_prazo=3, protocolo_ha=7,
    telefone="(27) 99000-0006",
    outorgados="Letícia Andrade Bueno",
    marcados={d: True for d in DOCS_BASE},
    pendencias=[("Enviar minuta por e-mail para conferência do casal", 1,
                 "Rafaela Bittencourt", "pendente")])

add(7, "2026-0849", "Eduarda Pimentel Rocha",
    ["Procuração para venda de imóvel"], "aguardando_assinatura", "Marina Salles",
    mostra="certidao de onus A VENCER (aviso de 5 dias) + depende do usuario",
    dias_prazo=-1, protocolo_ha=10,
    telefone="(27) 99000-0007",
    outorgados="Imobiliária Serra Azul Ltda.",
    onus_dias=3,
    marcados={d: True for d in DOCS_BASE} | {"Matrícula atualizada do imóvel": True,
                                             "Certidão de ônus reais": True},
    observacoes=[("Cliente vem assinar na sexta pela manhã.", 2, None)])

add(8, "2026-0852", "Gustavo Freire Antunes",
    ["Procuração para venda de imóvel"], "em_confeccao", "Rafaela Bittencourt",
    mostra="certidao de onus VENCIDA — precisa de certidao nova + pendencia de HOJE",
    dias_prazo=4, protocolo_ha=5,
    telefone="(27) 99000-0008",
    onus_dias=-6,
    outorgados="Marcos Vinícius Delgado",
    marcados={d: True for d in DOCS_BASE},
    pendencias=[("Pedir certidão de ônus atualizada no Registro de Imóveis", 0,
                 "Rafaela Bittencourt", "pendente")])

add(9, "2026-0853", "Construtora Pedra Branca S/A",
    ["Procuração para venda de imóvel"], "aguardando_documentos", "Marina Salles",
    mostra="exige onus e a data de emissao ainda nao foi informada",
    tipo_pessoa="pj", docs_completos=False, protocolo_ha=3,
    onus_sem_data=True,
    canais=["email", "balcao"],
    documento="00.000.000/0001-91",
    email="juridico@pedrabranca.exemplo.com.br")

add(10, "2026-0855", "Sônia Rezende Vilela",
    ["Escritura de Compra e Venda"], "em_analise", "Tiago Mendonça",
    mostra="par vinculado + certidao de onus EM DIA (o quarto estado, sem alarme)",
    dias_prazo=1, protocolo_ha=9,
    telefone="(27) 99000-0010",
    grupo=GRUPO_VINCULO,
    valor=315000.0,
    onus_dias=18,
    pendencias=[("Conferir o valor do ITBI recolhido", 3, "Tiago Mendonça", "pendente")],
    marcados={d: True for d in DOCS_BASE} | {"Matrícula atualizada do imóvel": True,
                                             "Comprovante de pagamento do ITBI": True})

add(11, "2026-0856", "Sônia Rezende Vilela",
    ["Procuração Ad Negotia"], "finalizado", "Tiago Mendonça",
    mostra="a outra metade do vinculo, ja finalizada e digitalizada",
    dias_prazo=-4, protocolo_ha=16,
    telefone="(27) 99000-0010",
    grupo=GRUPO_VINCULO,
    digitalizado=True,
    outorgados="Sônia Rezende Vilela",
    marcados={d: True for d in DOCS_BASE})

add(12, "2026-0858", "Padaria Dois Irmãos Ltda. ME",
    ["Escritura Declaratória"], "finalizado", "Rafaela Bittencourt",
    mostra="FINALIZADO mas sem digitalizar — nao pode arquivar ainda",
    tipo_pessoa="pj", dias_prazo=-2, protocolo_ha=13,
    digitalizado=False,
    documento="00.000.000/0001-72",
    canais=["balcao"],
    observacoes=[("Falta escanear o rascunho assinado antes de arquivar.", 1, None)])

add(13, "2026-0860", "Ana Lúcia Barcelos Pinto",
    ["Escritura de Divórcio Consensual"], "desistiu", "Marina Salles",
    mostra="fase final sem exigir digitalizacao",
    dias_prazo=-6, protocolo_ha=20,
    telefone="(27) 99000-0013",
    observacoes=[("Casal desistiu — vão tentar acordo pela via judicial.", 5, None)])

add(14, "2026-0862", "Henrique Salgado Moreira",
    ["Procuração Ad Judicia"], "em_confeccao", "Marina Salles",
    mostra="no prazo, folgado — o caso comum, que precisa aparecer",
    dias_prazo=4, protocolo_ha=4,
    telefone="(27) 99000-0014",
    outorgados="Dra. Priscila Tavares Rangel",
    marcados={d: True for d in DOCS_BASE})

add(15, "2026-0829", "Lançamento duplicado — conferir",
    ["Procuração Ad Judicia"], "aguardando_documentos", "Rafaela Bittencourt",
    mostra="lixeira: excluir nunca apaga, so move para ca",
    docs_completos=False, protocolo_ha=15,
    na_lixeira=True, excluido_ha=4)


# ------------------------------------------------------------------ tarefas
tarefas = [
    {
        "id": "tdemo01",
        "tipo": "checklist",
        "descricao": "Procuração de Beatriz Nogueira Sampaio",
        "data": iso(desloca(HOJE, 0)),
        "status": "pendente",
        "createdAt": ts(HOJE - timedelta(days=1), 15, 0),
        "concluidoEm": None,
        "protocoloRelacionadoId": "pdemo03",
        "numeroLivro": "412",
        "folha": "087",
        "etapas": [
            {"key": "verificar_sistema", "label": "Verificar no sistema",
             "feita": True, "ts": ts(HOJE - timedelta(days=1), 15, 30)},
            {"key": "levar_tabeliao", "label": "Levar ao tabelião para anotação no sistema",
             "feita": False, "ts": None},
            {"key": "anotar_livro", "label": "Anotar no livro", "feita": False, "ts": None,
             "subetapas": [
                 {"key": "assinatura", "label": "Levado para assinatura do tabelião",
                  "feita": False, "ts": None},
                 {"key": "guardado", "label": "Devolvido assinado e guardado",
                  "feita": False, "ts": None},
             ]},
        ],
    },
    {
        "id": "tdemo02",
        "tipo": "substabelecimento",
        "descricao": "Substabelecimento recebido de outra serventia",
        "data": iso(desloca(HOJE, 1)),
        "status": "pendente",
        "createdAt": ts(HOJE, 9, 0),
        "concluidoEm": None,
        "protocoloRelacionadoId": None,
        "origemAto": "outro_cartorio",
        "numeroLivro": "",
        "folha": "",
        "etapas": [
            {"key": "verificar_sistema", "label": "Verificar no sistema", "feita": False, "ts": None},
            {"key": "levar_tabeliao", "label": "Levar ao tabelião para anotação no sistema",
             "feita": False, "ts": None},
            {"key": "comunicar_cartorio_origem", "label": "Comunicar Cartório de origem",
             "feita": False, "ts": None, "subetapas": [
                 {"key": "oficio_comunicacao", "label": "Confecção de Ofício de Comunicação",
                  "feita": False, "ts": None},
                 {"key": "malote_enviado", "label": "Malote digital enviado pelo Tabelião",
                  "feita": False, "ts": None},
             ]},
        ],
    },
    {
        "id": "tdemo03",
        "tipo": "livre",
        "descricao": "Conferir a numeração do livro 412 antes do fechamento do mês",
        "data": iso(desloca(HOJE, 2)),
        "status": "pendente",
        "createdAt": ts(HOJE, 9, 5),
        "concluidoEm": None,
        "protocoloRelacionadoId": None,
    },
]

# ------------------------------------------------------- atos de balcao
# Doze dias uteis para tras, para o grafico ter forma. Numeros plausiveis para
# uma serventia de porte medio, variando por dia da semana.
atos_balcao = {}
atos_balcao_lancamentos = {}
_padrao = [14, 9, 11, 17, 8, 12, 15, 10, 13, 7, 16, 11]
for i, qtd in enumerate(_padrao):
    d = menos_dias_uteis(desloca(HOJE, 0), i)
    atos_balcao[iso(d)] = qtd
    # dois lancamentos no dia: manha e tarde, como acontece de verdade
    manha = qtd // 2
    atos_balcao_lancamentos[iso(d)] = [
        {"qtd": manha, "ts": ts(d, 11, 45)},
        {"qtd": qtd - manha, "ts": ts(d, 17, 20)},
    ]

# --------------------------------------------------------------- montagem
state = {
    "protocolos": protocolos,
    "tarefas": tarefas,
    "tiposAtos": TIPOS,
    "responsaveis": RESPONSAVEIS,
    "ultimoResponsavel": RESPONSAVEIS[0],
    "documentosChecklist": ["RG", "CPF", "Comprovante de residência",
                            "Certidão de casamento/nascimento"],
    "feriadosExtras": [],
    "feriadosMoveis": {"carnaval": True, "corpusChristi": True, "sextaSanta": True},
    "atosBalcao": atos_balcao,
    "atosBalcaoLancamentos": atos_balcao_lancamentos,
    "sugestoesDispensadas": {},
    "categoriaPorTipo": {t: ("procuracao" if t.startswith("Procuração") else "escritura")
                         for t in TIPOS},
    "checklistPorTipo": CHECKLIST_POR_TIPO,
    "exigeOnusPorTipo": {"Procuração para venda de imóvel": True,
                         "Escritura de Compra e Venda": True},
}

# statusList fica de fora de proposito: sem a chave, migrate() semeia a lista
# padrao de 8 fases. Fixar aqui congelaria a demonstracao numa versao antiga
# das fases assim que alguem editar DEFAULT_STATUS_LIST.

destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados-demo.json")
with open(destino, "w", encoding="utf-8") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

vivos = [p for p in protocolos if not p["naLixeira"]]
print("Gerado: %s" % destino)
print("  %d protocolos (%d na lista, %d na lixeira)"
      % (len(protocolos), len(vivos), len(protocolos) - len(vivos)))
print("  %d tarefas, %d dias de atos de balcão" % (len(tarefas), len(atos_balcao)))
if HOJE != _HOJE_REAL:
    print("  datas ancoradas em %s (hoje, %s, não é dia útil)" % (iso(HOJE), iso(_HOJE_REAL)))
else:
    print("  datas ancoradas em %s" % iso(HOJE))
