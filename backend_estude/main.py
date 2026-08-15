from auth import criar_hash_senha, verificar_senha
from fastapi import FastAPI, Depends, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import (
    engine,
    Base,
    SessionLocal,
    atualizar_banco
)

from models import Assinante, Progresso

from assinaturas import criar_assinatura
from webhook import router as webhook_router

from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime


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


# Atualiza automaticamente as novas colunas
# do cadastro no banco existente.
atualizar_banco()


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
    nome: str = Form(...),
    cpf: str = Form(...),
    cep: str = Form(...),
    rua: str = Form(...),
    numero: str = Form(...),
    bairro: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...),
    complemento: str = Form(""),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):

    novo_assinante = Assinante(

        nome=nome,

        cpf=cpf,

        cep=cep,

        rua=rua,

        numero=numero,

        bairro=bairro,

        cidade=cidade,

        estado=estado,

        complemento=complemento,

        email=email,

        senha=criar_hash_senha(senha),

        status="pendente"

    )


    db.add(novo_assinante)


    try:

        db.commit()

    except IntegrityError:

        db.rollback()

        return {
            "erro": "Já existe uma conta cadastrada com este e-mail"
        }


    db.refresh(novo_assinante)


    return {

        "mensagem": "Usuário criado",

        "id": novo_assinante.id

    }


@app.post("/login")
def login(
    email: str = Form(...),
    senha: str = Form(...),
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
    email: str = Form(...),
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


@app.get("/certificado")
def certificado(
    email: str,
    trilha: str,
    db: Session = Depends(get_db)
):

    usuario = db.query(Assinante).filter(
        Assinante.email == email
    ).first()


    if not usuario:

        return {
            "erro": "Usuário não encontrado"
        }


    certificados = {

        "python": {
            "nome": "TRILHA PYTHON",
            "horas": 60,
            "codigo": "PY"
        },

        "projetos": {
            "nome": "TRILHA ANALISTA DE PROJETOS",
            "horas": 80,
            "codigo": "GP"
        },

        "ia": {
            "nome": "TRILHA INTELIGÊNCIA ARTIFICIAL",
            "horas": 70,
            "codigo": "IA"
        },

        "cloud": {
            "nome": "TRILHA CLOUD & DEVOPS",
            "horas": 80,
            "codigo": "CL"
        },

        "geral": {
            "nome": "CERTIFICAÇÃO PROFISSIONAL CPG",
            "horas": 290,
            "codigo": "PRO"
        }

    }


    if trilha not in certificados:

        return {
            "erro": "Trilha inválida"
        }


    dados = certificados[trilha]


    if trilha == "geral":

        trilhas_concluidas = 0


        for nome_trilha in (
            "python",
            "ia",
            "cloud",
            "projetos"
        ):

            total = db.query(Progresso).filter(

                Progresso.assinante_id == usuario.id,

                Progresso.trilha == nome_trilha,

                Progresso.concluido == True

            ).count()


            if total >= 6:

                trilhas_concluidas += 1


        if trilhas_concluidas < 4:

            return {
                "erro": "Certificação profissional ainda não liberada"
            }


        return {

            "aluno": usuario.nome,

            "cpf": usuario.cpf,

            "cep": usuario.cep,

            "rua": usuario.rua,

            "numero": usuario.numero,

            "bairro": usuario.bairro,

            "cidade": usuario.cidade,

            "estado": usuario.estado,

            "complemento": usuario.complemento,

            "trilha": dados["nome"],

            "horas": dados["horas"],

            "codigo": f'CPG-{dados["codigo"]}-{usuario.id:05d}',

            "data": datetime.now().strftime("%d/%m/%Y")

        }


    concluidas = db.query(Progresso).filter(

        Progresso.assinante_id == usuario.id,

        Progresso.trilha == trilha,

        Progresso.concluido == True

    ).count()


    if concluidas < 6:

        return {

            "erro": "Trilha ainda não concluída"

        }


    return {

        "aluno": usuario.nome,

        "cpf": usuario.cpf,

        "cep": usuario.cep,

        "rua": usuario.rua,

        "numero": usuario.numero,

        "bairro": usuario.bairro,

        "cidade": usuario.cidade,

        "estado": usuario.estado,

        "complemento": usuario.complemento,

        "trilha": dados["nome"],

        "horas": dados["horas"],

        "codigo": f'CPG-{dados["codigo"]}-{usuario.id:05d}',

        "data": datetime.now().strftime("%d/%m/%Y")

    }


@app.post("/concluir-apostila")
def concluir_apostila(
    email: str = Form(...),
    trilha: str = Form(...),
    apostila: int = Form(...),
    db: Session = Depends(get_db)
):

    usuario = db.query(Assinante).filter(
        Assinante.email == email
    ).first()


    if not usuario:

        return {
            "erro": "Usuário não encontrado"
        }


    progresso = db.query(Progresso).filter(

        Progresso.assinante_id == usuario.id,

        Progresso.trilha == trilha,

        Progresso.apostila == apostila

    ).first()


    if progresso:

        progresso.concluido = True


    else:

        progresso = Progresso(

            assinante_id=usuario.id,

            trilha=trilha,

            apostila=apostila,

            concluido=True

        )

        db.add(progresso)


    db.commit()


    return {

        "mensagem": "Apostila concluída"

    }


@app.get("/progresso")
def progresso(
    email: str,
    trilha: str,
    db: Session = Depends(get_db)
):

    usuario = db.query(Assinante).filter(
        Assinante.email == email
    ).first()


    if not usuario:

        return {
            "erro": "Usuário não encontrado"
        }


    progresso = db.query(Progresso).filter(

        Progresso.assinante_id == usuario.id,

        Progresso.trilha == trilha,

        Progresso.concluido == True

    ).all()


    return {

        "apostilas": [
            item.apostila
            for item in progresso
        ]

    }