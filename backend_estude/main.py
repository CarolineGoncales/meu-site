from auth import criar_hash_senha, verificar_senha
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models import Assinante
from auth import criar_hash_senha

from assinaturas import criar_assinatura
from webhook import router as webhook_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CPG Estude Comigo"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)

Base.metadata.create_all(
    bind=engine
)



def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



@app.get("/")
def inicio():

    return {
        "status": "online",
        "sistema": "CPG Estude Comigo"
    }



@app.post("/cadastro")
def cadastro(
    nome: str,
    email: str,
    senha: str,
    db: Session = Depends(get_db)
):

    novo_assinante = Assinante(
        nome=nome,
        email=email,
        senha=criar_hash_senha(senha),
        status="pendente"
    )

    db.add(novo_assinante)

    db.commit()

    db.refresh(novo_assinante)

    return {
        "mensagem": "Usuário criado",
        "id": novo_assinante.id
    }



@app.post("/login")
def login(
    email: str,
    senha: str,
    db: Session = Depends(get_db)
):

    usuario = db.query(Assinante).filter(
        Assinante.email == email
    ).first()


    if not usuario:
        return {
            "erro": "Usuário não encontrado"
        }


    senha_valida = verificar_senha(
        senha,
        usuario.senha
    )


    if not senha_valida:
        return {
            "erro": "Senha inválida"
        }


    if usuario.status != "ativo":
        return {
            "erro": "Assinatura pendente"
        }


    return {
    "mensagem": "Login realizado",
    "usuario": usuario.nome,
    "email": usuario.email,
    "status": usuario.status,
    "status_pagamento": usuario.status_pagamento,
    "plano": usuario.plano
}



@app.post("/criar-assinatura")
def assinatura(
    email: str,
    db: Session = Depends(get_db)
):

    usuario = db.query(Assinante).filter(
        Assinante.email == email
    ).first()


    if not usuario:
        return {
            "erro": "Usuário não encontrado"
        }


    resultado = criar_assinatura(email)


    if resultado["status"] != 201:

        return {
            "erro": "Erro ao criar assinatura",
            "dados": resultado
        }


    assinatura_mp = resultado["response"]


    usuario.assinatura_id = assinatura_mp["id"]

    usuario.mercado_pago_id = str(
        assinatura_mp["payer_id"]
    )

    usuario.status_pagamento = "pendente"


    db.commit()


    return {
        "mensagem": "Assinatura criada e vinculada",
        "assinatura_id": usuario.assinatura_id,
        "status": usuario.status_pagamento,
        "checkout": assinatura_mp["init_point"]
    }
    
@app.post("/criar-root")
def criar_root(
    db: Session = Depends(get_db)
    ):

    usuario_existente = db.query(Assinante).filter(
        Assinante.email == "SEU_EMAIL_AQUI"
    ).first()


    if usuario_existente:
        return {
            "erro": "Usuário já existe",
            "email": usuario_existente.email
        }


    novo_usuario = Assinante(

        nome="Caroline Admin",

        email="caroline_perez1@live.com",

        senha=criar_hash_senha("123456"),

        status="ativo",

        status_pagamento="aprovado",

        plano="Estude Comigo Mensal"

    )


    db.add(novo_usuario)

    db.commit()

    db.refresh(novo_usuario)


    return {

        "mensagem": "Usuário root criado",

        "email": novo_usuario.email,

        "senha_temporaria": "123456"

    }