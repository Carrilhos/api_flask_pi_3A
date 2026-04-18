from app.repositories.produto_repository import (
    find_all_produtos,
    find_produto_by_id,
    get_category_attributes
)

def get_all_produtos():
    produtos = find_all_produtos()
    category_attributes = get_category_attributes()
    print(category_attributes)
    
    for produto in produtos:
        produto["atributos"] = []
        for cat_attr in category_attributes:
            if cat_attr["id_categoria"] == produto["id_categoria"]:
                produto["atributos"].append({cat_attr["nome_atributo"]: "dado temporario"}) # Substitua "valor" pelo valor real do atributo para o produto
    # print(produtos)
    return produtos

def get_produto_by_id(id_produto):

    produto = find_produto_by_id(id_produto)

    if not produto:
        return None

    return produto