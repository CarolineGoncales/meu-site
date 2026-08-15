import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./assinantes.db"
)


if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )


opcoes = (
    {"connect_args": {"check_same_thread": False}}
    if DATABASE_URL.startswith("sqlite")
    else {}
)


engine = create_engine(
    DATABASE_URL,
    **opcoes
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def atualizar_banco():

    with engine.begin() as conexao:

        colunas = [
            ("cpf", "VARCHAR"),
            ("cep", "VARCHAR"),
            ("rua", "VARCHAR"),
            ("numero", "VARCHAR"),
            ("bairro", "VARCHAR"),
            ("cidade", "VARCHAR"),
            ("estado", "VARCHAR"),
            ("complemento", "VARCHAR")
        ]

        for nome, tipo in colunas:

            if DATABASE_URL.startswith("postgresql"):

                conexao.execute(
                    text(
                        f"""
                        ALTER TABLE assinantes
                        ADD COLUMN IF NOT EXISTS {nome} {tipo}
                        """
                    )
                )

            else:

                resultado = conexao.execute(
                    text("PRAGMA table_info(assinantes)")
                )

                existentes = [
                    coluna[1]
                    for coluna in resultado.fetchall()
                ]

                if nome not in existentes:

                    conexao.execute(
                        text(
                            f"""
                            ALTER TABLE assinantes
                            ADD COLUMN {nome} {tipo}
                            """
                        )
                    )