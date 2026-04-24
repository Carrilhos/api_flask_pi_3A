from app.repositories.produto_repository import (
    find_all_produtos,
    find_produto_by_id,
    get_category_attributes,
    get_atributos_por_produto,
)

def get_all_produtos():
    # Busca todos os produtos
    produtos = find_all_produtos()
    
    for produto in produtos:
        produto["atributos"] = []
        
        rows_atributos = get_atributos_por_produto(produto["id_produto"])
        
        for attr in rows_atributos:
            nome_attr = attr[0]
            val_str = attr[1]
            val_num = attr[2]
            val_bool = attr[3]
            
            # Descobre qual valor está preenchido
            valor_final = val_str if val_str is not None else (val_num if val_num is not None else val_bool)
            
            produto["atributos"].append({ nome_attr: valor_final })

    return produtos

def get_produto_by_id(id_produto):
    produto = find_produto_by_id(id_produto)

    if not produto:
        return None
        
    produto["atributos"] = []
    rows_atributos = get_atributos_por_produto(id_produto)
    
    for attr in rows_atributos:
        nome_attr = attr[0]
        val_str = attr[1]
        val_num = attr[2]
        val_bool = attr[3]
        valor_final = val_str if val_str is not None else (val_num if val_num is not None else val_bool)
        produto["atributos"].append({ nome_attr: valor_final })

    return produto