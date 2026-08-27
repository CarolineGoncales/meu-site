# =========================================================
# PAGBANK - CPG ESTUDE COMIGO
# =========================================================

import os


# =========================================================
# LINK DA ASSINATURA RECORRENTE
# =========================================================

PAGBANK_LINK_RECORRENTE = os.getenv(
    "PAGBANK_LINK_RECORRENTE",
    "https://pag.ae/826qXWwB5"
)


# =========================================================
# CRIAR ASSINATURA
# =========================================================

def criar_assinatura(email_cliente):

    if not PAGBANK_LINK_RECORRENTE:

        return {
            "status": 400,

            "response": {
                "erro":
                    "Link de assinatura do PagBank não configurado"
            }
        }


    return {

        "status": 201,

        "response": {

            "checkout_url":
                PAGBANK_LINK_RECORRENTE,

            "email":
                email_cliente,

            "gateway":
                "pagbank"

        }

    }