import mercadopago

from config import MERCADO_PAGO_ACCESS_TOKEN


sdk = mercadopago.SDK(
    MERCADO_PAGO_ACCESS_TOKEN
)


def criar_assinatura(
    email_cliente
):

    plano = {
    "reason": "CPG Estude Comigo",
    "external_reference": email_cliente,

    "back_url": "https://cpgconsulting.com.br/obrigado.html",

    "auto_recurring": {
        "frequency": 1,
        "frequency_type": "months",
        "transaction_amount": 9.99,
        "currency_id": "BRL"
    },

    "payer_email": email_cliente
}


    resposta = sdk.preapproval().create(
        plano
    )


    return resposta


def consultar_assinatura(assinatura_id):
    return sdk.preapproval().get(assinatura_id)
