from app.repositories.anuncio_repository import (
    create_anuncio,
    get_dados_basicos_anuncio_produto,
    get_imagens_por_anuncio,
    get_atributos_por_produto
)

from app.repositories.produto_imagem_repository import inserir_imagem
from app.services.upload_service import upload_imagem_supabase


def _campos_obrigatorios(data: dict, campos: list):
    faltando = [c for c in campos if c not in data or data[c] is None]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None


def criar_anuncio_service(data, imagens=None, imagem_principal=0):
    if not data:
        raise ValueError("Form data inválido.")

    ok, erro = _campos_obrigatorios(
        data,
        ["id_vendedor", "id_produto", "titulo", "preco"]
    )

    if not ok:
        raise ValueError(erro)

    # validar preço
    try:
        preco = float(data["preco"])
        if preco < 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError("preco deve ser um número positivo.")

    # validar estoque
    estoque = data.get("estoque", 0)

    try:
        estoque = int(estoque)
        if estoque < 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError(
            "estoque deve ser um número inteiro não negativo."
        )

    # cria anúncio
    anuncio = create_anuncio(
        id_vendedor=data["id_vendedor"],
        id_produto=data["id_produto"],
        titulo=str(data["titulo"])[:255],
        descricao=data.get("descricao"),
        preco=round(preco, 2),
        estoque=estoque,
    )

    id_anuncio = anuncio["id_anuncio"]

    # se não houver imagens, retorna direto
    if not imagens or len(imagens) == 0:
        return anuncio

    # valida índice da principal
    try:
        imagem_principal = int(imagem_principal)
    except (ValueError, TypeError):
        imagem_principal = 0

    if imagem_principal < 0 or imagem_principal >= len(imagens):
        imagem_principal = 0

    imagens_salvas = []

    for index, imagem in enumerate(imagens):

        # upload para o bucket imagens (Supabase)
        url = upload_imagem_supabase(
            imagem=imagem,
            id_anuncio=id_anuncio,
            index=index
        )

        inserir_imagem(
            id_produto=data["id_produto"],
            id_anuncio=id_anuncio,
            url=url,
            nome_arquivo=imagem.filename,
            principal=(index == imagem_principal),
            ordem=index
        )

        imagens_salvas.append({
            "url": url,
            "principal": index == imagem_principal,
            "ordem": index
        })

    anuncio["imagens"] = imagens_salvas

    return anuncio

def obter_anuncio_completo(id_anuncio):
    # Busca os dados brutos no Repository
    row_anuncio = get_dados_basicos_anuncio_produto(id_anuncio)
    
    if not row_anuncio:
        return None

    # Monta o esqueleto principal
    anuncio_dict = {
        "id_anuncio": row_anuncio[0],
        "titulo": row_anuncio[1],
        "descricao": row_anuncio[2],
        "preco": float(row_anuncio[3]) if row_anuncio[3] else 0.0,
        "estoque": row_anuncio[4],
        "imagem_principal": None,
        "produto": {
            "id_produto": row_anuncio[5],
            "nome": row_anuncio[6],
            "marca": row_anuncio[7],
            "modelo": row_anuncio[8],
            "fabricante": row_anuncio[9],
            "id_categoria": row_anuncio[10]
        },
        "imagens": [],
        "atributos": []
    }
    
    id_produto = row_anuncio[5]

    # Busca e processa as imagens
    rows_imagens = get_imagens_por_anuncio(id_anuncio)
    for img in rows_imagens:
        url_imagem = img[0]
        is_principal = img[1]
        
        anuncio_dict["imagens"].append(url_imagem)
        if is_principal:
            anuncio_dict["imagem_principal"] = url_imagem

    # Se não tem imagem principal, pega a primeira
    if not anuncio_dict["imagem_principal"] and anuncio_dict["imagens"]:
        anuncio_dict["imagem_principal"] = anuncio_dict["imagens"][0]

    # Busca e processa os atributos
    if id_produto:
        rows_atributos = get_atributos_por_produto(id_produto)
        for attr in rows_atributos:
            nome_attr = attr[0]
            val_str = attr[1]
            val_num = attr[2]
            val_bool = attr[3]
            
            # descobrir qual valor está preenchido
            valor_final = val_str if val_str is not None else (val_num if val_num is not None else val_bool)
            
            anuncio_dict["atributos"].append({ nome_attr: valor_final })

    return anuncio_dict