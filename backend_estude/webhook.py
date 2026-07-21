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



@router.post("/webhook")
async def webhook(
    request: Request,
    db: Session = Depends(get_db)
):

    dados = await request.json()

    print("Webhook recebido:")
    print(dados)


    return {
        "status": "recebido"
    }