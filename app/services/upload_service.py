import uuid
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET = "imagens"

def upload_imagem_supabase(imagem, id_anuncio, index):
    if not imagem:
        return None

    extensao = imagem.filename.split(".")[-1].lower()
    nome_arquivo = f"{uuid.uuid4()}_{index}.{extensao}"

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    url_upload = f"{supabase_url}/storage/v1/object/{BUCKET}/{nome_arquivo}"

    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": imagem.content_type,
    }

    response = requests.post(url_upload, headers=headers, data=imagem.read())

    if response.status_code not in (200, 201):
        raise Exception(f"Erro upload Supabase: {response.text}")

    url_publica = f"{supabase_url}/storage/v1/object/public/{BUCKET}/{nome_arquivo}"

    return url_publica
