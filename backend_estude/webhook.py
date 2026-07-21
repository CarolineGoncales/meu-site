from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from database import SessionLocal


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

    except Exception:

        dados = {}



    print("Webhook recebido:")
    print(dados)


    return {
        "status": "recebido",
        "dados": dados
    }