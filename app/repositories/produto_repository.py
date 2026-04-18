from app.database import get_connection


def find_all_produtos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
                   SELECT   id_produto,
                            nome,
                            descricao,
                            marca,
                            modelo,
                            fabricante,
                            id_categoria
                   FROM produto
                   WHERE ativo = true
                   """
    )

    rows = cursor.fetchall()

    print(rows)

    cursor.close()
    conn.close()

    # converter tupla -> dict
    produtos = []

    for row in rows:
        produtos.append(
            {
                "id_produto": row[0],
                "nome": row[1],
                "descricao": row[2],
                "marca": row[3],
                "modelo": row[4],
                "fabricante": row[5],
                "id_categoria": row[6],
            }
        )

    return produtos


def get_category_attributes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
                   SELECT a.nome AS nome_atributo,
                          c.id   AS id_categoria
                   FROM atributo a
                            JOIN categoria_atributo ca ON
                       ca.id_atributo = a.id_atributo
                            JOIN categoria c ON
                       c.id = ca.id_categoria
                   """
    )
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    category_attributes = []

    for row in rows:
        category_attributes.append(
            {
                "nome_atributo": row[0],
                "id_categoria": row[1]
            }
        )

    return category_attributes
    



def find_produto_by_id(id_produto):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
                   SELECT *
                   FROM produto
                   WHERE id_produto = %s
                   """,
        (id_produto,),
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id_produto": row[0],
        "nome": row[1],
        "descricao": row[2],
        "marca": row[3],
        "modelo": row[4],
        "id_categoria": row[5],
        "ativo": row[6],
        "data_criacao": row[7],
        "data_atualizacao": row[8],
        "fabricante": row[9],
    }
