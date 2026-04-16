from app.repositories.produto_repository import (
    find_all_produtos,
    find_produto_by_id
)

def get_all_produtos():
    produtos = find_all_produtos()

    return produtos

def get_produto_by_id(id_produto):

    produto = find_produto_by_id(id_produto)

    if not produto:
        return None

    return produto