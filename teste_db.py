import os
from dotenv import load_dotenv
from app.database import get_connection

print(os.getenv("DATABASE_URL"))
try:
    conn = get_connection()

    print("Conectado com sucesso!")

    conn.close()

except Exception as e:
    print("Erro ao conectar:")
    print(e)