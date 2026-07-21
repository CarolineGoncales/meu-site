import mercadopago

from config import MERCADO_PAGO_ACCESS_TOKEN


sdk = mercadopago.SDK(
    MERCADO_PAGO_ACCESS_TOKEN
)


def consultar_pagamento(payment_id):

    pagamento = sdk.payment().get(
        payment_id
    )

    return pagamento