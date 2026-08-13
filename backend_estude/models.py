from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base


class Assinante(Base):

    __tablename__ = "assinantes"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    nome = Column(
        String,
        nullable=False
    )


    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )


    senha = Column(
        String,
        nullable=False
    )


    status = Column(
        String,
        default="pendente"
    )


    status_pagamento = Column(
        String,
        default="pendente"
    )


    mercado_pago_id = Column(
        String,
        nullable=True
    )


    assinatura_id = Column(
        String,
        nullable=True
    )


    plano = Column(
        String,
        default="Estude Comigo Mensal"
    )


    data_inicio = Column(
        String,
        nullable=True
    )


    proximo_pagamento = Column(
        String,
        nullable=True
    )


    ultimo_pagamento = Column(
        String,
        nullable=True
    )
    
class Progresso(Base):

    __tablename__ = "progresso"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    assinante_id = Column(
        Integer,
        ForeignKey("assinantes.id"),
        nullable=False
    )


    trilha = Column(
        String,
        nullable=False
    )


    apostila = Column(
        Integer,
        nullable=False
    )


    concluido = Column(
        Boolean,
        default=False
    )    