from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)



def criar_hash_senha(senha):

    return pwd_context.hash(senha)



def verificar_senha(
    senha_digitada,
    senha_hash
):

    return pwd_context.verify(
        senha_digitada,
        senha_hash
    )