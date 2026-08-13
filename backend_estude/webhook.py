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

    # A notificação apenas informa o identificador. O status confiável é
    # consultado novamente na API do Mercado Pago antes de atualizar o aluno.
    assinatura_id = (
        dados.get("data", {}).get("id")
        or request.query_params.get("id")
        or dados.get("id")
    )

    tipo = dados.get("type") or dados.get("topic")
    if not assinatura_id or tipo not in ("subscription_preapproval", "preapproval"):
        return {"status": "ignorado"}

    resultado = consultar_assinatura(str(assinatura_id))
    if resultado.get("status") != 200:
        return {"status": "erro_consulta"}

    assinatura = resultado.get("response", {})
    usuario = db.query(Assinante).filter(
        Assinante.assinatura_id == str(assinatura_id)
    ).first()

    if not usuario:
        return {"status": "assinatura_nao_encontrada"}

    status_mp = assinatura.get("status", "pendente")
    usuario.status_pagamento = status_mp
    usuario.status = "ativo" if status_mp == "authorized" else "pendente"
    usuario.ultimo_pagamento = assinatura.get("last_modified")
    usuario.proximo_pagamento = assinatura.get("next_payment_date")
    db.commit()

    return {
        "status": "atualizado",
        "assinatura": str(assinatura_id),
        "status_pagamento": status_mp
    }
