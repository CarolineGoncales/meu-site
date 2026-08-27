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


    print("========================================")
    print("WEBHOOK PAGBANK RECEBIDO")
    print("DADOS:", dados)
    print("========================================")


    # =====================================================
    # EVENTO
    # =====================================================

    evento = dados.get("event")

    resource = dados.get(
        "resource",
        {}
    )


    # =====================================================
    # ESTRUTURA DO PAGBANK
    # =====================================================

    if not isinstance(resource, dict):
        resource = {}


    # =====================================================
    # TENTA LOCALIZAR OS DADOS DO CLIENTE
    # =====================================================

    cliente = resource.get(
        "customer",
        {}
    )

    if not isinstance(cliente, dict):
        cliente = {}


    email = cliente.get("email")


    # Alguns eventos podem trazer o e-mail
    # em outra parte da estrutura.

    if not email:

        email = resource.get("email")


    if not email:

        email = dados.get("email")


    # =====================================================
    # ID DA ASSINATURA
    # =====================================================

    assinatura_id = (
        resource.get("id")
        or resource.get("subscription_id")
        or dados.get("subscription_id")
    )


    # =====================================================
    # STATUS
    # =====================================================

    status_assinatura = (
        resource.get("status")
        or dados.get("status")
    )


    print("EVENTO:", evento)
    print("ASSINATURA:", assinatura_id)
    print("EMAIL:", email)
    print("STATUS:", status_assinatura)


    # =====================================================
    # SEM E-MAIL
    # =====================================================

    if not email:

        return {
            "status": "email_nao_encontrado"
        }


    email = email.strip().lower()


    # =====================================================
    # PROCURA O ALUNO
    # =====================================================

    usuario = db.query(
        Assinante
    ).filter(
        Assinante.email == email
    ).first()


    if not usuario:

        print(
            "ALUNO NÃO ENCONTRADO:",
            email
        )

        return {

            "status":
                "usuario_nao_encontrado",

            "email":
                email

        }


    # =====================================================
    # SALVA ID DA ASSINATURA
    # =====================================================

    if assinatura_id:

        usuario.assinatura_id = str(
            assinatura_id
        )


    # =====================================================
    # PAGAMENTO / ASSINATURA APROVADA
    # =====================================================

    eventos_aprovados = (

        "subscription.activated",

        "subscription.initial",

        "subscription.recurrence",

        "charge.paid",

        "charge.completed",

        "payment.paid",

        "payment.approved"

    )


    status_aprovados = (

        "ACTIVE",

        "PAID",

        "COMPLETED",

        "APPROVED",

        "AUTHORIZED",

        "AVAILABLE"

    )


    if (

        evento in eventos_aprovados

        or status_assinatura in status_aprovados

    ):

        usuario.status = "ativo"

        usuario.status_pagamento = "active"


        usuario.ultimo_pagamento = (

            resource.get(
                "updated_at"
            )

            or resource.get(
                "paid_at"
            )

            or dados.get(
                "created_at"
            )

        )


        usuario.proximo_pagamento = (

            resource.get(
                "next_invoice_at"
            )

            or resource.get(
                "next_payment_at"
            )

        )


        db.commit()


        print(
            "========================================"
        )

        print(
            "PAGAMENTO CONFIRMADO"
        )

        print(
            "ALUNO:",
            usuario.email
        )

        print(
            "ACESSO: LIBERADO"
        )

        print(
            "========================================"
        )


        return {

            "status":
                "pagamento_aprovado",

            "usuario":
                usuario.email,

            "acesso":
                "liberado"

        }


    # =====================================================
    # PAGAMENTO PENDENTE
    # =====================================================

    eventos_pendentes = (

        "subscription.pending",

        "charge.pending",

        "payment.pending",

        "payment.in_analysis",

        "payment.in_analysis"

    )


    status_pendentes = (

        "PENDING",

        "IN_ANALYSIS",

        "WAITING",

        "PROCESSING"

    )


    if (

        evento in eventos_pendentes

        or status_assinatura in status_pendentes

    ):

        usuario.status = "pendente"

        usuario.status_pagamento = "pending"


        db.commit()


        return {

            "status":
                "pagamento_pendente",

            "usuario":
                usuario.email,

            "acesso":
                "bloqueado"

        }


    # =====================================================
    # PAGAMENTO RECUSADO
    # =====================================================

    eventos_recusados = (

        "charge.failed",

        "charge.declined",

        "payment.failed",

        "payment.declined",

        "subscription.suspended"

    )


    status_recusados = (

        "FAILED",

        "DECLINED",

        "DENIED",

        "REJECTED",

        "SUSPENDED"

    )


    if (

        evento in eventos_recusados

        or status_assinatura in status_recusados

    ):

        usuario.status = "pendente"

        usuario.status_pagamento = "failed"


        db.commit()


        print(
            "PAGAMENTO RECUSADO:",
            usuario.email
        )


        return {

            "status":
                "pagamento_recusado",

            "usuario":
                usuario.email,

            "acesso":
                "bloqueado"

        }


    # =====================================================
    # ASSINATURA CANCELADA
    # =====================================================

    if evento in (

        "subscription.canceled",

        "subscription.cancelled",

        "subscription.expired",

        "subscription.terminated"

    ):

        usuario.status = "pendente"

        usuario.status_pagamento = "canceled"


        db.commit()


        return {

            "status":
                "assinatura_cancelada",

            "usuario":
                usuario.email,

            "acesso":
                "bloqueado"

        }


    # =====================================================
    # ASSINATURA SUSPENSA
    # =====================================================

    if evento in (

        "subscription.suspended",

        "subscription.paused"

    ):

        usuario.status = "pendente"

        usuario.status_pagamento = "suspended"


        db.commit()


        return {

            "status":
                "assinatura_suspensa",

            "usuario":
                usuario.email,

            "acesso":
                "bloqueado"

        }


    # =====================================================
    # EVENTO DESCONHECIDO
    # =====================================================

    print(
        "EVENTO NÃO TRATADO:",
        evento
    )


    return {

        "status":
            "evento_recebido",

        "evento":
            evento,

        "usuario":
            usuario.email

    }