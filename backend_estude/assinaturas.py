# =========================================================
# PAGAMENTO - CPG ESTUDE COMIGO
# PAGBANK
# =========================================================

PAGBANK_LINK_RECORRENTE = "https://pag.ae/826qXWwB5"


def criar_assinatura(email_cliente):

    return {
        "status": 201,
        "response": {
            "checkout_url": PAGBANK_LINK_RECORRENTE,
            "email": email_cliente
        }
    }