from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Assinante

import json

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

    print("=================================")
    print("WEBHOOK MERCADO PAGO")
    print(json.dumps(dados, indent=4))
    print("=================================")

    return {
        "status": "recebido",
        "dados": dados
    }