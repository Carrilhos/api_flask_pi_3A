import uuid
import requests
import os
from dotenv import load_dotenv
from app.config import Config

load_dotenv()

BUCKET = "imagens"

def upload_imagem_supabase(imagem, id_anuncio, index):
    if not imagem:
        return None

    # extrai extensão
    extensao = imagem.filename.split(".")[-1].lower()
    
    # nome único
    nome_arquivo = f"{uuid.uuid4()}_{index}.{extensao}"

    url_upload = f"{os.getenv("SUPABASE_URL")}/storage/v1/object/{BUCKET}/{nome_arquivo}"

    headers = {
        "Authorization": f"Bearer {os.getenv("SUPABASE_SERVICE_KEY")}",
        "Content-Type": imagem.content_type
    }

    response = requests.post(
        url_upload,
        headers=headers,
        data=imagem.read()
    )

    if response.status_code not in (200, 201):
        raise Exception(f"Erro upload Supabase: {response.text}")

    # bucket público
    url_publica = (
        f"{os.getenv("SUPABASE_URL")}/storage/v1/object/public/"
        f"{BUCKET}/{nome_arquivo}"
    )

    return url_publica