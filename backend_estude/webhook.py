from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Assinante

from assinaturas import (
    consultar_assinatura,
    consultar_pagamento
)


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


    tipo = (
        dados.get("type")
        or dados.get("topic")
    )


    # =========================================================
    # PAGAMENTO
    # =========================================================

    if tipo == "payment":

        pagamento_id = (
            dados.get("data", {}).get("id")
            or request.query_params.get("id")
            or dados.get("id")
        )


        if not pagamento_id:

            return {
                "status": "pagamento_id_nao_encontrado"
            }


        # Consulta o pagamento diretamente no Mercado Pago

        resultado = consultar_pagamento(
            str(pagamento_id)
        )


        if resultado.get("status") != 200:

            return {
                "status": "erro_consulta_pagamento"
            }


        pagamento = resultado.get(
            "response",
            {}
        )


        status_pagamento = pagamento.get(
            "status"
        )


        # =====================================================
        # IDENTIFICA O E-MAIL DO CLIENTE
        # =====================================================

        payer = pagamento.get(
            "payer",
            {}
        )


        email = payer.get(
            "email"
        )


        # Alguns pagamentos podem trazer o e-mail
        # em external_reference.

        if not email:

            email = pagamento.get(
                "external_reference"
            )


        usuario = None


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

                    break


        # =====================================================
        # USUÁRIO NÃO ENCONTRADO
        # =====================================================

        if not usuario:

            return {

                "status": "usuario_nao_encontrado",

                "pagamento": str(
                    pagamento_id
                ),

                "email": email

            }


        # =====================================================
        # PAGAMENTO APROVADO
        # =====================================================

        if status_pagamento == "approved":

            usuario.status = "ativo"

            usuario.status_pagamento = "approved"

            usuario.ultimo_pagamento = pagamento.get(
                "date_approved"
            )


            db.commit()


            return {

                "status": "atualizado",

                "tipo": "payment",

                "pagamento": str(
                    pagamento_id
                ),

                "status_pagamento":
                    status_pagamento,

                "usuario":
                    usuario.email,

                "acesso":
                    "liberado"

            }


        # =====================================================
        # PAGAMENTO NÃO APROVADO
        # =====================================================

        usuario.status_pagamento = (
            status_pagamento
            or "pending"
        )


        db.commit()


        return {

            "status":
                "pagamento_nao_aprovado",

            "pagamento":
                str(pagamento_id),

            "status_pagamento":
                status_pagamento

        }


    # =========================================================
    # ASSINATURA
    # =========================================================

    if tipo in (
        "subscription_preapproval",
        "preapproval"
    ):

        assinatura_id = (
            dados.get("data", {}).get("id")
            or request.query_params.get("id")
            or dados.get("id")
        )


        if not assinatura_id:

            return {

                "status":
                    "assinatura_id_nao_encontrado"

            }


        # Consulta a assinatura diretamente
        # no Mercado Pago.

        resultado = consultar_assinatura(
            str(assinatura_id)
        )


        if resultado.get("status") != 200:

            return {

                "status":
                    "erro_consulta_assinatura"

            }


        assinatura = resultado.get(
            "response",
            {}
        )


        # =====================================================
        # PRIMEIRO TENTA PELO ID DA ASSINATURA
        # =====================================================

        usuario = db.query(
            Assinante
        ).filter(

            Assinante.assinatura_id
            == str(assinatura_id)

        ).first()


        # =====================================================
        # SE NÃO ENCONTROU, TENTA PELO E-MAIL
        # =====================================================

        if not usuario:

            email = (
                assinatura.get(
                    "external_reference"
                )
                or assinatura.get(
                    "payer_email"
                )
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


        # =====================================================
        # ASSINATURA NÃO ENCONTRADA
        # =====================================================

        if not usuario:

            return {

                "status":
                    "assinatura_nao_encontrada"

            }


        # =====================================================
        # ATUALIZA STATUS DA ASSINATURA
        # =====================================================

        status_mp = assinatura.get(
            "status",
            "pending"
        )


        usuario.status_pagamento = status_mp


        if status_mp == "authorized":

            usuario.status = "ativo"

        else:

            usuario.status = "pendente"


        usuario.ultimo_pagamento = assinatura.get(
            "last_modified"
        )


        usuario.proximo_pagamento = assinatura.get(
            "next_payment_date"
        )


        db.commit()


        return {

            "status":
                "atualizado",

            "tipo":
                "subscription",

            "assinatura":
                str(assinatura_id),

            "status_pagamento":
                status_mp

        }


    # =========================================================
    # OUTROS EVENTOS
    # =========================================================

    return {

        "status":
            "ignorado"

    }