from app.database import get_connection

def find_all_produtos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            *
        FROM produto
        ORDER BY id_produto
    """)

    rows = cursor.fetchall()

    print(rows)

    cursor.close()
    conn.close()

    # converter tupla -> dict
    produtos = []

    for row in rows:
        produtos.append({
            "id_produto": row[0],
            "nome": row[1],
            "descricao": row[2],
            "marca": row[3],
            "modelo": row[4],
            "id_categoria": row[5],
            "ativo": row[6],
            "data_criacao": row[7],
            "data_atualizacao": row[8],
            "fabricante": row[9]
        })

    return produtos


def find_produto_by_id(id_produto):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
           *
        FROM produto
        WHERE id_produto = %s
    """, (id_produto,))

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
        "fabricante": row[9]
    }