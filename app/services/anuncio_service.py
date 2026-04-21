from app.repositories.anuncio_repository import create_anuncio
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