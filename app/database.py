import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_connection():
    """Estabelece e retorna uma conexão ativa com o banco de dados PostgreSQL usando a URL definida no arquivo .env."""
    return psycopg2.connect(os.getenv("DATABASE_URL"))