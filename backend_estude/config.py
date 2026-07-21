import os
from dotenv import load_dotenv


load_dotenv()


MERCADO_PAGO_ACCESS_TOKEN = os.getenv(
    "MERCADO_PAGO_ACCESS_TOKEN"
)


MERCADO_PAGO_PUBLIC_KEY = os.getenv(
    "MERCADO_PAGO_PUBLIC_KEY"
)