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

from datetime import datetime, timedelta

import secrets
import hashlib
import json
import urllib.request
import urllib.error

from sqlalchemy import Column, Integer, String, DateTime, Boolean


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



# ==========================================
# TOKENS DE RECUPERAÇÃO DE SENHA
# ==========================================

class ResetSenha(Base):

    __tablename__ = "reset_senhas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    assinante_id = Column(
        Integer,
        nullable=False
    )

    token_hash = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    expiracao = Column(
        DateTime,
        nullable=False
    )

    usado = Column(
        Boolean,
        default=False,
        nullable=False
    )


# Cria a tabela caso ainda não exista
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
    
# ==========================================
# ENVIO DE E-MAIL DE RECUPERAÇÃO
# ==========================================

def enviar_email_reset(email, nome, link):

    dados = {

        "service_id": "service_g4z931k",

        "template_id": "template_off1d5f",

        "user_id": "jjCZK1jHx4tRtfUiS",

        "template_params": {

            "email": email,

            "name": nome,

            "link": link

        }

    }

    corpo = json.dumps(dados).encode("utf-8")

    requisicao = urllib.request.Request(

        "https://api.emailjs.com/api/v1.0/email/send",

        data=corpo,

        headers={
            "Content-Type": "application/json"
        },

        method="POST"

    )

    try:

        with urllib.request.urlopen(
            requisicao,
            timeout=15
        ) as resposta:

            status = resposta.status

            conteudo = resposta.read().decode(
                "utf-8"
            )

            if status != 200:

                raise Exception(
                    f"EmailJS retornou HTTP {status}: {conteudo}"
                )

            return True

    except urllib.error.HTTPError as erro:

        detalhes = erro.read().decode(
            "utf-8",
            errors="ignore"
        )

        print(
            "ERRO EMAILJS:",
            erro.code,
            detalhes
        )

        return False

    except Exception as erro:

        print(
            "ERRO AO ENVIAR E-MAIL:",
            erro
        )

        return False    

# ==========================================
# SOLICITAR RECUPERAÇÃO DE SENHA
# ==========================================

@app.post("/solicitar-reset")
def solicitar_reset(
    email: str = Form(...),
    db: Session = Depends(get_db)
):

    email = email.strip().lower()

    usuario = db.query(Assinante).filter(
        Assinante.email == email
    ).first()

    # Não revela se o e-mail existe ou não
    if not usuario:

        return {
            "mensagem":
            "Se o e-mail estiver cadastrado, "
            "você receberá em instantes "
            "as instruções para redefinir sua senha."
        }

    # Invalida solicitações anteriores
    tokens_antigos = db.query(
        ResetSenha
    ).filter(
        ResetSenha.assinante_id == usuario.id,
        ResetSenha.usado == False
    ).all()

    for token_antigo in tokens_antigos:
        token_antigo.usado = True

    # Gera um novo token
    token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    expiracao = (
        datetime.utcnow()
        + timedelta(hours=1)
    )

    novo_reset = ResetSenha(
        assinante_id=usuario.id,
        token_hash=token_hash,
        expiracao=expiracao,
        usado=False
    )

    db.add(novo_reset)

    db.commit()

    # Link que será enviado por e-mail
    link = (
        "https://cpgconsulting.com.br/"
        "nova-senha.html?token="
        + token
    )

    # Envia pelo EmailJS
    enviado = enviar_email_reset(
        email=usuario.email,
        nome=usuario.nome,
        link=link
    )

    if not enviado:

        print(
            "Não foi possível enviar "
            "o e-mail de recuperação para:",
            usuario.email
        )

    return {
        "mensagem":
        "Se o e-mail estiver cadastrado, "
        "você receberá em instantes "
        "as instruções para redefinir sua senha."
    }

# ==========================================
# ALTERAR SENHA COM TOKEN
# ==========================================

@app.post("/alterar-senha")
def alterar_senha(
    token: str = Form(...),
    nova_senha: str = Form(...),
    db: Session = Depends(get_db)
):

    # --------------------------------------
    # Validação básica da senha
    # --------------------------------------

    if len(nova_senha) < 6:

        return {
            "erro":
            "A nova senha deve possuir pelo menos 6 caracteres."
        }


    # --------------------------------------
    # Gera o hash do token recebido
    # --------------------------------------

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


    # --------------------------------------
    # Procura o token
    # --------------------------------------

    reset = db.query(
        ResetSenha
    ).filter(

        ResetSenha.token_hash == token_hash,

        ResetSenha.usado == False

    ).first()


    if not reset:

        return {
            "erro":
            "Este link de recuperação é inválido ou já foi utilizado."
        }


    # --------------------------------------
    # Verifica validade
    # --------------------------------------

    if datetime.utcnow() > reset.expiracao:

        reset.usado = True

        db.commit()

        return {
            "erro":
            "Este link de recuperação expirou. Solicite uma nova alteração de senha."
        }


    # --------------------------------------
    # Procura o usuário
    # --------------------------------------

    usuario = db.query(
        Assinante
    ).filter(

        Assinante.id == reset.assinante_id

    ).first()


    if not usuario:

        reset.usado = True

        db.commit()

        return {
            "erro":
            "Usuário não encontrado."
        }


    # --------------------------------------
    # Altera a senha usando hash
    # --------------------------------------

    usuario.senha = criar_hash_senha(
        nova_senha
    )


    # --------------------------------------
    # Invalida o token
    # --------------------------------------

    reset.usado = True


    db.commit()


    return {

        "mensagem":
        "Senha alterada com sucesso."

    }    
    
@app.get("/meus-dados")
def meus_dados(
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

    return {
        "nome": usuario.nome,
        "cpf": usuario.cpf,
        "cep": usuario.cep,
        "rua": usuario.rua,
        "numero": usuario.numero,
        "bairro": usuario.bairro,
        "cidade": usuario.cidade,
        "estado": usuario.estado,
        "complemento": usuario.complemento,
        "email": usuario.email
    }


@app.post("/meus-dados")
def atualizar_meus_dados(
    nome: str = Form(...),
    cpf: str = Form(...),
    cep: str = Form(...),
    rua: str = Form(...),
    numero: str = Form(...),
    bairro: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...),
    complemento: str = Form(""),
    nova_senha: str = Form(""),
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

    usuario.nome = nome
    usuario.cpf = cpf
    usuario.cep = cep
    usuario.rua = rua
    usuario.numero = numero
    usuario.bairro = bairro
    usuario.cidade = cidade
    usuario.estado = estado
    usuario.complemento = complemento

    if nova_senha.strip():
        usuario.senha = criar_hash_senha(nova_senha)

    db.commit()
    db.refresh(usuario)

    return {
        "mensagem": "Dados atualizados com sucesso",
        "nome": usuario.nome
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

@app.get("/validar-certificado")
def validar_certificado(
    codigo: str,
    db: Session = Depends(get_db)
):

    # ===============================
    # CÓDIGO DEVE TER O FORMATO:
    # CPG-PY-00001
    # CPG-GP-00001
    # CPG-IA-00001
    # CPG-CL-00001
    # CPG-PRO-00001
    # ===============================

    partes = codigo.split("-")

    if len(partes) != 3:

        return {
            "erro": "Código de certificado inválido"
        }


    prefixo = partes[0]

    codigo_trilha = partes[1]

    try:

        usuario_id = int(partes[2])

    except ValueError:

        return {
            "erro": "Código de certificado inválido"
        }


    if prefixo != "CPG":

        return {
            "erro": "Código de certificado inválido"
        }


    # ===============================
    # RELAÇÃO DOS CÓDIGOS
    # ===============================

    trilhas = {

        "PY": {
            "nome": "TRILHA PYTHON",
            "horas": 60,
            "trilha": "python"
        },

        "GP": {
            "nome": "TRILHA ANALISTA DE PROJETOS",
            "horas": 80,
            "trilha": "projetos"
        },

        "IA": {
            "nome": "TRILHA INTELIGÊNCIA ARTIFICIAL",
            "horas": 70,
            "trilha": "ia"
        },

        "CL": {
            "nome": "TRILHA CLOUD & DEVOPS",
            "horas": 80,
            "trilha": "cloud"
        },

        "PRO": {
            "nome": "CERTIFICAÇÃO PROFISSIONAL CPG",
            "horas": 290,
            "trilha": "geral"
        }

    }


    if codigo_trilha not in trilhas:

        return {
            "erro": "Código de certificado inválido"
        }


    dados_trilha = trilhas[codigo_trilha]


    # ===============================
    # PROCURA O ALUNO
    # ===============================

    usuario = db.query(Assinante).filter(
        Assinante.id == usuario_id
    ).first()


    if not usuario:

        return {
            "erro": "Certificado não encontrado"
        }


    # ===============================
    # VERIFICA CONCLUSÃO
    # ===============================

    if dados_trilha["trilha"] == "geral":

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
                "erro": "Certificado ainda não liberado"
            }


    else:

        total = db.query(Progresso).filter(

            Progresso.assinante_id == usuario.id,

            Progresso.trilha == dados_trilha["trilha"],

            Progresso.concluido == True

        ).count()


        if total < 6:

            return {
                "erro": "Certificado ainda não liberado"
            }


    # ===============================
    # CERTIFICADO VÁLIDO
    # ===============================

    return {

        "valido": True,

        "aluno": usuario.nome,

        "cpf": usuario.cpf,

        "trilha": dados_trilha["nome"],

        "horas": dados_trilha["horas"],

        "codigo": codigo,

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