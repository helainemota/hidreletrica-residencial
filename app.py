from flask import Flask, render_template
from datetime import datetime
import json
import os
import random

app = Flask(__name__)

# ============================================================
# ARQUIVO DE HISTÓRICO
# ============================================================

ARQUIVO_HISTORICO = "dados/historico.json"


# ============================================================
# REFERÊNCIAS DO PROJETO
# ============================================================
# Estes valores vêm do cenário definido no documento do projeto.
# Eles representam REFERÊNCIAS/DIMENSIONAMENTO e não medições.

CONSUMO_DIARIO_REFERENCIA = 7.65
CONSUMO_MENSAL_REFERENCIA = 229.5

VAZAO_REFERENCIA_LS = 8.0
VAZAO_REFERENCIA_M3S = 0.008

DESNIVEL_REFERENCIA = 10.0

RENDIMENTO_GLOBAL = 0.70

DENSIDADE_AGUA = 1000.0
GRAVIDADE = 9.81

HORAS_OPERACAO_DIA = 15
DIAS_MES = 30


# ============================================================
# CÁLCULO DO DIMENSIONAMENTO DE REFERÊNCIA
# ============================================================

def calcular_referencia():

    # Potência hidráulica:
    # Ph = ρ × g × Q × H

    potencia_hidraulica = (
        DENSIDADE_AGUA
        * GRAVIDADE
        * VAZAO_REFERENCIA_M3S
        * DESNIVEL_REFERENCIA
    )

    # Potência elétrica:
    # Pel = Ph × η

    potencia_eletrica = (
        potencia_hidraulica
        * RENDIMENTO_GLOBAL
    )

    potencia_eletrica_kw = (
        potencia_eletrica / 1000
    )

    # Energia diária:
    # E = P × t

    energia_diaria = (
        potencia_eletrica_kw
        * HORAS_OPERACAO_DIA
    )

    # Energia mensal

    energia_mensal = (
        energia_diaria
        * DIAS_MES
    )

    # Cobertura teórica da demanda

    cobertura = (
        energia_diaria
        / CONSUMO_DIARIO_REFERENCIA
    ) * 100

    # Excedente mensal teórico

    excedente = (
        energia_mensal
        - CONSUMO_MENSAL_REFERENCIA
    )

    return {
        "consumo_diario": CONSUMO_DIARIO_REFERENCIA,
        "consumo_mensal": CONSUMO_MENSAL_REFERENCIA,

        "vazao_ls": VAZAO_REFERENCIA_LS,
        "vazao_m3s": VAZAO_REFERENCIA_M3S,

        "desnivel": DESNIVEL_REFERENCIA,

        "rendimento": RENDIMENTO_GLOBAL,

        "densidade": DENSIDADE_AGUA,
        "gravidade": GRAVIDADE,

        "horas_operacao": HORAS_OPERACAO_DIA,

        "potencia_hidraulica": round(
            potencia_hidraulica,
            2
        ),

        "potencia_eletrica": round(
            potencia_eletrica,
            2
        ),

        "potencia_eletrica_kw": round(
            potencia_eletrica_kw,
            5
        ),

        "energia_diaria": round(
            energia_diaria,
            4
        ),

        "energia_mensal": round(
            energia_mensal,
            3
        ),

        "cobertura": round(
            cobertura,
            2
        ),

        "excedente": round(
            excedente,
            3
        )
    }


# ============================================================
# SIMULAÇÃO DE MONITORAMENTO
# ============================================================
# Estes valores representam uma demonstração de como o sistema
# poderia receber dados de sensores.
#
# IMPORTANTE:
# Eles NÃO são medições reais da residência.

def gerar_monitoramento():

    referencia = calcular_referencia()

    # Pequenas variações para simular o comportamento do sistema

    vazao_atual = round(
        random.uniform(7.4, 8.4),
        2
    )

    nivel_reservatorio = round(
        random.uniform(65, 95),
        1
    )

    # A potência atual é relacionada à vazão simulada.
    #
    # Isso não representa um modelo físico completo.
    # É apenas uma simulação para demonstrar o sistema.

    fator_vazao = (
        vazao_atual
        / referencia["vazao_ls"]
    )

    potencia_atual = round(
        referencia["potencia_eletrica"]
        * fator_vazao
        * random.uniform(0.96, 1.02),
        2
    )

    potencia_atual_kw = round(
        potencia_atual / 1000,
        3
    )

    # Consumo residencial simulado

    consumo_atual = round(
        random.uniform(0.25, 0.60),
        2
    )

    # Energia acumulada no dia simulada

    energia_hoje = round(
        potencia_atual_kw
        * random.uniform(7, 15),
        2
    )

    return {
        "nivel_reservatorio": nivel_reservatorio,

        "vazao_atual": vazao_atual,

        "potencia_atual": potencia_atual,

        "potencia_atual_kw": potencia_atual_kw,

        "consumo_atual": consumo_atual,

        "energia_hoje": energia_hoje,

        "horario": datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        ),

        "origem": "SIMULAÇÃO"
    }


# ============================================================
# ANÁLISE DO NÍVEL DO RESERVATÓRIO
# ============================================================

def analisar_nivel(nivel):

    if nivel >= 70:

        return {
            "status": "NORMAL",
            "classe": "normal",
            "mensagem": (
                "O nível do reservatório está "
                "dentro da faixa operacional simulada."
            )
        }

    elif nivel >= 50:

        return {
            "status": "ATENÇÃO",
            "classe": "atencao",
            "mensagem": (
                "O nível do reservatório está "
                "abaixo da faixa normal simulada."
            )
        }

    else:

        return {
            "status": "CRÍTICO",
            "classe": "critico",
            "mensagem": (
                "O nível do reservatório está "
                "muito baixo."
            )
        }


# ============================================================
# ANÁLISE DA POTÊNCIA
# ============================================================

def analisar_potencia(potencia_atual, potencia_referencia):

    limite_atencao = potencia_referencia * 0.90
    limite_critico = potencia_referencia * 0.75

    if potencia_atual >= limite_atencao:

        return {
            "status": "NORMAL",
            "classe": "normal",
            "mensagem": (
                "A potência está próxima do "
                "valor de referência."
            )
        }

    elif potencia_atual >= limite_critico:

        return {
            "status": "ATENÇÃO",
            "classe": "atencao",
            "mensagem": (
                "A potência está abaixo do valor "
                "de referência e merece acompanhamento."
            )
        }

    else:

        return {
            "status": "CRÍTICO",
            "classe": "critico",
            "mensagem": (
                "A potência está significativamente "
                "abaixo do valor de referência."
            )
        }


# ============================================================
# ANÁLISE DA VAZÃO
# ============================================================

def analisar_vazao(vazao_atual, vazao_referencia):

    diferenca_percentual = (
        (vazao_atual - vazao_referencia)
        / vazao_referencia
    ) * 100

    if vazao_atual >= vazao_referencia * 0.90:

        status = "NORMAL"
        classe = "normal"

        mensagem = (
            "A vazão está próxima do valor "
            "de referência do projeto."
        )

    elif vazao_atual >= vazao_referencia * 0.75:

        status = "ATENÇÃO"
        classe = "atencao"

        mensagem = (
            "A vazão está abaixo do valor "
            "de referência."
        )

    else:

        status = "CRÍTICO"
        classe = "critico"

        mensagem = (
            "A vazão está significativamente "
            "abaixo do valor de referência."
        )

    return {
        "status": status,
        "classe": classe,
        "mensagem": mensagem,
        "diferenca": round(
            diferenca_percentual,
            1
        )
    }


# ============================================================
# GERAÇÃO DOS ALERTAS
# ============================================================

def gerar_alertas(monitoramento, referencia):

    alertas = []

    analise_nivel = analisar_nivel(
        monitoramento["nivel_reservatorio"]
    )

    analise_potencia = analisar_potencia(
        monitoramento["potencia_atual"],
        referencia["potencia_eletrica"]
    )

    analise_vazao = analisar_vazao(
        monitoramento["vazao_atual"],
        referencia["vazao_ls"]
    )


    # --------------------------------------------------------
    # ALERTA DE NÍVEL
    # --------------------------------------------------------

    if analise_nivel["classe"] != "normal":

        alertas.append({
            "tipo": analise_nivel["classe"],
            "titulo": (
                "Nível do reservatório "
                + analise_nivel["status"].lower()
            ),
            "mensagem": analise_nivel["mensagem"]
        })


    # --------------------------------------------------------
    # ALERTA DE POTÊNCIA
    # --------------------------------------------------------

    if analise_potencia["classe"] != "normal":

        alertas.append({
            "tipo": analise_potencia["classe"],
            "titulo": (
                "Potência "
                + analise_potencia["status"].lower()
            ),
            "mensagem": analise_potencia["mensagem"]
        })


    # --------------------------------------------------------
    # ALERTA DE VAZÃO
    # --------------------------------------------------------

    if analise_vazao["classe"] != "normal":

        alertas.append({
            "tipo": analise_vazao["classe"],
            "titulo": (
                "Vazão "
                + analise_vazao["status"].lower()
            ),
            "mensagem": analise_vazao["mensagem"]
        })


    # --------------------------------------------------------
    # SE NÃO HOUVER ALERTAS
    # --------------------------------------------------------

    if len(alertas) == 0:

        alertas.append({
            "tipo": "normal",
            "titulo": "Sistema operando normalmente",
            "mensagem": (
                "Os parâmetros monitorados estão "
                "dentro das faixas utilizadas."
            )
        })


    return alertas


# ============================================================
# STATUS GERAL
# ============================================================

def calcular_status_geral(alertas):

    tipos = [
        alerta["tipo"]
        for alerta in alertas
    ]

    if "critico" in tipos:

        return {
            "texto": "ATENÇÃO NECESSÁRIA",
            "classe": "critico"
        }

    if "atencao" in tipos:

        return {
            "texto": "ACOMPANHAMENTO NECESSÁRIO",
            "classe": "atencao"
        }

    return {
        "texto": "SISTEMA NORMAL",
        "classe": "normal"
    }


# ============================================================
# DADOS COMPLETOS DO SISTEMA
# ============================================================

def gerar_dados_sistema():

    referencia = calcular_referencia()

    monitoramento = gerar_monitoramento()

    analise_nivel = analisar_nivel(
        monitoramento["nivel_reservatorio"]
    )

    analise_potencia = analisar_potencia(
        monitoramento["potencia_atual"],
        referencia["potencia_eletrica"]
    )

    analise_vazao = analisar_vazao(
        monitoramento["vazao_atual"],
        referencia["vazao_ls"]
    )

    alertas = gerar_alertas(
        monitoramento,
        referencia
    )

    status_geral = calcular_status_geral(
        alertas
    )


    return {

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        "status": status_geral["texto"],
        "classe_status": status_geral["classe"],

        # ----------------------------------------------------
        # MONITORAMENTO ATUAL
        # ----------------------------------------------------

        "nivel_reservatorio":
            monitoramento["nivel_reservatorio"],

        "vazao_atual":
            monitoramento["vazao_atual"],

        "potencia_atual":
            monitoramento["potencia_atual"],

        "potencia_atual_kw":
            monitoramento["potencia_atual_kw"],

        "consumo_atual":
            monitoramento["consumo_atual"],

        "energia_hoje":
            monitoramento["energia_hoje"],

        "horario":
            monitoramento["horario"],

        "origem":
            monitoramento["origem"],

        # ----------------------------------------------------
        # ANÁLISES
        # ----------------------------------------------------

        "analise_nivel":
            analise_nivel,

        "analise_potencia":
            analise_potencia,

        "analise_vazao":
            analise_vazao,

        # ----------------------------------------------------
        # REFERÊNCIAS
        # ----------------------------------------------------

        "potencia_referencia":
            referencia["potencia_eletrica"],

        "potencia_referencia_kw":
            referencia["potencia_eletrica_kw"],

        "vazao_referencia":
            referencia["vazao_ls"],

        "desnivel":
            referencia["desnivel"],

        "rendimento":
            referencia["rendimento"],

        "energia_diaria_referencia":
            referencia["energia_diaria"],

        "energia_mensal_referencia":
            referencia["energia_mensal"],

        "consumo_diario":
            referencia["consumo_diario"],

        "consumo_mensal":
            referencia["consumo_mensal"],

        "cobertura_referencia":
            referencia["cobertura"],

        "excedente_referencia":
            referencia["excedente"],

        # ----------------------------------------------------
        # ALERTAS
        # ----------------------------------------------------

        "alertas":
            alertas
    }


# ============================================================
# HISTÓRICO
# ============================================================

def registrar_historico(dados):

    pasta = os.path.dirname(
        ARQUIVO_HISTORICO
    )

    os.makedirs(
        pasta,
        exist_ok=True
    )


    if os.path.exists(
        ARQUIVO_HISTORICO
    ):

        try:

            with open(
                ARQUIVO_HISTORICO,
                "r",
                encoding="utf-8"
            ) as arquivo:

                historico = json.load(
                    arquivo
                )

        except (
            json.JSONDecodeError,
            FileNotFoundError
        ):

            historico = []

    else:

        historico = []


    registro = {

        "horario":
            dados["horario"],

        "nivel":
            dados["nivel_reservatorio"],

        "vazao":
            dados["vazao_atual"],

        "potencia":
            dados["potencia_atual"],

        "consumo":
            dados["consumo_atual"],

        "energia":
            dados["energia_hoje"],

        "status":
            dados["status"],

        "origem":
            dados["origem"]
    }


    historico.append(
        registro
    )

    historico = historico[-100:]


    with open(
        ARQUIVO_HISTORICO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            historico,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def ler_historico():

    if not os.path.exists(
        ARQUIVO_HISTORICO
    ):

        return []


    try:

        with open(
            ARQUIVO_HISTORICO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(
                arquivo
            )

    except (
        json.JSONDecodeError,
        FileNotFoundError
    ):

        return []


# ============================================================
# MANUTENÇÃO
# ============================================================

def gerar_manutencoes(dados):

    manutencoes = []


    # --------------------------------------------------------
    # RESERVATÓRIO
    # --------------------------------------------------------

    if (
        dados["analise_nivel"]["classe"]
        != "normal"
    ):

        manutencoes.append({

            "equipamento":
                "Reservatório",

            "prioridade":
                dados["analise_nivel"]["status"],

            "classe":
                dados["analise_nivel"]["classe"],

            "descricao":
                "Verificar o nível do reservatório "
                "e investigar a causa da redução."
        })


    # --------------------------------------------------------
    # VAZÃO
    # --------------------------------------------------------

    if (
        dados["analise_vazao"]["classe"]
        != "normal"
    ):

        manutencoes.append({

            "equipamento":
                "Sistema hidráulico",

            "prioridade":
                dados["analise_vazao"]["status"],

            "classe":
                dados["analise_vazao"]["classe"],

            "descricao":
                "Verificar captação, tubulação, "
                "obstruções e possíveis perdas "
                "hidráulicas."
        })


    # --------------------------------------------------------
    # POTÊNCIA
    # --------------------------------------------------------

    if (
        dados["analise_potencia"]["classe"]
        != "normal"
    ):

        manutencoes.append({

            "equipamento":
                "Turbina / Gerador",

            "prioridade":
                dados["analise_potencia"]["status"],

            "classe":
                dados["analise_potencia"]["classe"],

            "descricao":
                "Verificar as condições de funcionamento "
                "do conjunto de geração."
        })


    # --------------------------------------------------------
    # NENHUM PROBLEMA
    # --------------------------------------------------------

    if len(manutencoes) == 0:

        manutencoes.append({

            "equipamento":
                "Sistema geral",

            "prioridade":
                "NORMAL",

            "classe":
                "normal",

            "descricao":
                "Nenhuma condição de manutenção "
                "foi identificadas."
        })


    return manutencoes


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def inicio():

    dados = gerar_dados_sistema()

    return render_template(
        "index.html",
        dados=dados
    )


# ============================================================
# ENERGIA
# ============================================================

@app.route("/energia")
def energia():

    dados = gerar_dados_sistema()

    referencia = calcular_referencia()

    return render_template(
        "energia.html",
        dados=dados,
        energia=referencia
    )


# ============================================================
# ALERTAS
# ============================================================

@app.route("/alertas")
def alertas():

    dados = gerar_dados_sistema()

    return render_template(
        "alertas.html",
        dados=dados
    )


# ============================================================
# HISTÓRICO
# ============================================================

@app.route("/historico")
def historico():

    registros = ler_historico()

    return render_template(
        "historico.html",
        registros=registros
    )


# ============================================================
# EQUIPAMENTOS
# ============================================================

@app.route("/equipamentos")
def equipamentos():

    dados = gerar_dados_sistema()

    equipamentos = [

        {
            "nome":
                "Reservatório",

            "icone":
                "💧",

            "estado":
                dados["analise_nivel"]["status"],

            "classe":
                dados["analise_nivel"]["classe"],

            "parametros": [

                f'Nível atual: '
                f'{dados["nivel_reservatorio"]}%',

                f'Vazão: '
                f'{dados["vazao_atual"]} L/s'
            ],

            "mensagem":
                dados["analise_nivel"]["mensagem"]
        },

        {
            "nome":
                "Sistema hidráulico",

            "icone":
                "🔗",

            "estado":
                dados["analise_vazao"]["status"],

            "classe":
                dados["analise_vazao"]["classe"],

            "parametros": [

                f'Vazão atual: '
                f'{dados["vazao_atual"]} L/s',

                f'Referência: '
                f'{dados["vazao_referencia"]} L/s',

                f'Desnível de referência: '
                f'{dados["desnivel"]} m'
            ],

            "mensagem":
                dados["analise_vazao"]["mensagem"]
        },

        {
            "nome":
                "Turbina",

            "icone":
                "⚙️",

            "estado":
                dados["analise_potencia"]["status"],

            "classe":
                dados["analise_potencia"]["classe"],

            "parametros": [

                f'Potência atual: '
                f'{dados["potencia_atual"]} W',

                f'Referência: '
                f'{dados["potencia_referencia"]} W'
            ],

            "mensagem":
                dados["analise_potencia"]["mensagem"]
        },

        {
            "nome":
                "Gerador",

            "icone":
                "⚡",

            "estado":
                dados["analise_potencia"]["status"],

            "classe":
                dados["analise_potencia"]["classe"],

            "parametros": [

                f'Potência atual: '
                f'{dados["potencia_atual_kw"]} kW',

                f'Referência: '
                f'{dados["potencia_referencia_kw"]} kW'
            ],

            "mensagem":
                dados["analise_potencia"]["mensagem"]
        }
    ]


    return render_template(
        "equipamentos.html",
        dados=dados,
        equipamentos=equipamentos
    )


# ============================================================
# MANUTENÇÃO
# ============================================================

@app.route("/manutencao")
def manutencao():

    dados = gerar_dados_sistema()

    manutencoes = gerar_manutencoes(
        dados
    )

    return render_template(
        "manutencao.html",
        dados=dados,
        manutencoes=manutencoes
    )


# ============================================================
# API DE ATUALIZAÇÃO
# ============================================================

@app.route("/atualizar")
def atualizar():

    dados = gerar_dados_sistema()

    registrar_historico(
        dados
    )

    return {
        "sucesso": True,
        "dados": dados
    }


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )