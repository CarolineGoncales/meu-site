from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Assinante
from assinaturas import consultar_assinatura


router = APIRouter()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/webhook")
async def webhook(
    request: Request,
    db: Session = Depends(get_db)
):

    try:

        dados = await request.json()

    except:

        dados = {}


    # A notificação apenas informa o identificador.
    # O status confiável é consultado novamente
    # diretamente na API do Mercado Pago.

    assinatura_id = (
        dados.get("data", {}).get("id")
        or request.query_params.get("id")
        or dados.get("id")
    )


    tipo = dados.get("type") or dados.get("topic")


    if not assinatura_id or tipo not in (
        "subscription_preapproval",
        "preapproval"
    ):

        return {
            "status": "ignorado"
        }


    # Consulta a assinatura diretamente no Mercado Pago

    resultado = consultar_assinatura(
        str(assinatura_id)
    )


    if resultado.get("status") != 200:

        return {
            "status": "erro_consulta"
        }


    assinatura = resultado.get(
        "response",
        {}
    )


    # Primeiro tenta localizar pelo ID da assinatura

    usuario = db.query(Assinante).filter(

        Assinante.assinatura_id
        == str(assinatura_id)

    ).first()


    # Se não encontrou pelo ID,
    # tenta localizar pelo e-mail.
    #
    # O e-mail pode estar em external_reference
    # ou em payer_email.

    if not usuario:

        email = (
            assinatura.get("external_reference")
            or assinatura.get("payer_email")
        )


        if email:

            email = email.strip().lower()


            usuarios = db.query(
                Assinante
            ).all()


            for candidato in usuarios:

                if (
                    candidato.email
                    and candidato.email.strip().lower()
                    == email
                ):

                    usuario = candidato

                    usuario.assinatura_id = str(
                        assinatura_id
                    )

                    break


    # Se ainda não encontrou o usuário,
    # não há como atualizar a conta.

    if not usuario:

        return {
            "status": "assinatura_nao_encontrada"
        }


    # Status retornado pelo Mercado Pago

    status_mp = assinatura.get(
        "status",
        "pendente"
    )


    usuario.status_pagamento = status_mp


    # Assinatura autorizada = acesso liberado

    usuario.status = (
        "ativo"
        if status_mp == "authorized"
        else "pendente"
    )


    usuario.ultimo_pagamento = assinatura.get(
        "last_modified"
    )


    usuario.proximo_pagamento = assinatura.get(
        "next_payment_date"
    )


    db.commit()


    return {

        "status": "atualizado",

        "assinatura": str(
            assinatura_id
        ),

        "status_pagamento": status_mp

    }