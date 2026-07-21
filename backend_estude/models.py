from sqlalchemy import Column, Integer, String
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