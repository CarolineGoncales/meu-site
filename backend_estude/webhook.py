from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Assinante


router = APIRouter()


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =========================================================
# WEBHOOK PAGBANK
# =========================================================

@router.post("/webhook")
async def webhook(
    request: Request,
    db: Session = Depends(get_db)
):

    try:

        dados = await request.json()

    except Exception:

        dados = {}


    # =====================================================
    # EVENTO PAGBANK
    # =====================================================

    evento = dados.get(
        "event"
    )


    resource = dados.get(
        "resource",
        {}
    )


    # =====================================================
    # LOG PARA TESTES
    # =====================================================

    print(
        "========================================"
    )

    print(
        "WEBHOOK PAGBANK RECEBIDO"
    )

    print(
        "EVENTO:",
        evento
    )

    print(
        "DADOS:",
        dados
    )

    print(
        "========================================"
    )


    # =====================================================
    # IGNORA EVENTOS QUE NÃO SÃO DE ASSINATURA
    # =====================================================

    eventos_assinatura = (

        "subscription.initial",

        "subscription.updated",

        "subscription.activated",

        "subscription.suspended",

        "subscription.recurrence",

        "subscription.expired",

        "subscription.canceled",

        "subscription.migrated"

    )


    if evento not in eventos_assinatura:

        return {

            "status":
                "ignorado",

            "evento":
                evento

        }


    # =====================================================
    # DADOS DA ASSINATURA
    # =====================================================

    assinatura_id = resource.get(
        "id"
    )


    status_assinatura = resource.get(
        "status"
    )


    cliente = resource.get(
        "customer",
        {}
    )


    email = cliente.get(
        "email"
    )


    # =====================================================
    # VALIDAÇÃO
    # =====================================================

    if not assinatura_id:

        return {

            "status":
                "assinatura_id_nao_encontrado"

        }


    if not email:

        return {

            "status":
                "email_nao_encontrado",

            "assinatura":
                str(assinatura_id)

        }


    email = email.strip().lower()


    # =====================================================
    # PROCURA O ALUNO PELO E-MAIL
    # =====================================================

    usuario = db.query(
        Assinante
    ).filter(
        Assinante.email == email
    ).first()


    # =====================================================
    # ALUNO NÃO ENCONTRADO
    # =====================================================

    if not usuario:

        print(
            "ALUNO NÃO ENCONTRADO:",
            email
        )


        return {

            "status":
                "usuario_nao_encontrado",

            "email":
                email,

            "assinatura":
                str(assinatura_id)

        }


    # =====================================================
    # SALVA O ID DA ASSINATURA PAGBANK
    # =====================================================

    usuario.assinatura_id = (
        str(assinatura_id)
    )


    # =====================================================
    # ASSINATURA ATIVA
    # =====================================================

    if evento == "subscription.activated":

        usuario.status = (
            "ativo"
        )

        usuario.status_pagamento = (
            "active"
        )


        usuario.ultimo_pagamento = (
            resource.get(
                "updated_at"
            )
        )


        usuario.proximo_pagamento = (
            resource.get(
                "next_invoice_at"
            )
        )


        db.commit()


        print(
            "========================================"
        )

        print(
            "PAGAMENTO CONFIRMADO!"
        )

        print(
            "ALUNO:",
            usuario.email
        )

        print(
            "STATUS:",
            usuario.status
        )

        print(
            "========================================"
        )


        return {

            "status":
                "atualizado",

            "evento":
                evento,

            "usuario":
                usuario.email,

            "assinatura":
                str(assinatura_id),

            "acesso":
                "liberado"

        }


    # =====================================================
    # COBRANÇA RECORRENTE
    # =====================================================

    if evento == "subscription.recurrence":

        usuario.status_pagamento = (
            status_assinatura
            or "active"
        )


        # Se a cobrança recorrente
        # continua ativa, mantém o acesso.

        if status_assinatura == "ACTIVE":

            usuario.status = (
                "ativo"
            )


        else:

            usuario.status = (
                "pendente"
            )


        usuario.ultimo_pagamento = (
            resource.get(
                "updated_at"
            )
        )


        usuario.proximo_pagamento = (
            resource.get(
                "next_invoice_at"
            )
        )


        db.commit()


        return {

            "status":
                "recorrencia_processada",

            "usuario":
                usuario.email,

            "status_pagamento":
                status_assinatura

        }


    # =====================================================
    # ASSINATURA SUSPENSA
    # =====================================================

    if evento == "subscription.suspended":

        usuario.status = (
            "pendente"
        )

        usuario.status_pagamento = (
            "suspended"
        )


        db.commit()


        return {

            "status":
                "assinatura_suspensa",

            "usuario":
                usuario.email

        }


    # =====================================================
    # ASSINATURA CANCELADA
    # =====================================================

    if evento == "subscription.canceled":

        usuario.status = (
            "pendente"
        )

        usuario.status_pagamento = (
            "canceled"
        )


        db.commit()


        return {

            "status":
                "assinatura_cancelada",

            "usuario":
                usuario.email

        }


    # =====================================================
    # ASSINATURA EXPIRADA
    # =====================================================

    if evento == "subscription.expired":

        usuario.status = (
            "pendente"
        )

        usuario.status_pagamento = (
            "expired"
        )


        db.commit()


        return {

            "status":
                "assinatura_expirada",

            "usuario":
                usuario.email

        }


    # =====================================================
    # ASSINATURA INICIAL
    # =====================================================

    if evento == "subscription.initial":

        usuario.assinatura_id = (
            str(assinatura_id)
        )


        usuario.status_pagamento = (
            status_assinatura
            or "pending"
        )


        usuario.proximo_pagamento = (
            resource.get(
                "next_invoice_at"
            )
        )


        db.commit()


        return {

            "status":
                "assinatura_registrada",

            "usuario":
                usuario.email,

            "assinatura":
                str(assinatura_id)

        }


    # =====================================================
    # OUTROS EVENTOS
    # =====================================================

    usuario.status_pagamento = (
        status_assinatura
        or "pending"
    )


    db.commit()


    return {

        "status":
            "evento_processado",

        "evento":
            evento,

        "usuario":
            usuario.email

    }