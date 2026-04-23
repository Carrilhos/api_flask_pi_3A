def inserir_pedido_item(conn, id_pedido, id_anuncio, quantidade, preco):
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO pedido_item (
            id_pedido,
            id_anuncio,
            quantidade,
            preco
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id_pedido_item,
                  id_pedido,
                  id_anuncio,
                  quantidade,
                  preco,
                  data_criacao,
                  data_atualizacao
        """,
        (id_pedido, id_anuncio, quantidade, preco),
    )

    row = cursor.fetchone()
    cursor.close()

    return {
        "id_pedido_item":   row[0],
        "id_pedido":        row[1],
        "id_anuncio":       row[2],
        "quantidade":       row[3],
        "preco":            row[4],
        "data_criacao":     row[5],
        "data_atualizacao": row[6],
    }


def find_itens_by_pedido(id_pedido):
    from app.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_pedido_item,
                id_pedido,
                id_anuncio,
                quantidade,
                preco,
                data_criacao,
                data_atualizacao
        FROM pedido_item
        WHERE id_pedido = %s
        ORDER BY id_pedido_item
        """,
        (id_pedido,),
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "id_pedido_item":   row[0],
            "id_pedido":        row[1],
            "id_anuncio":       row[2],
            "quantidade":       row[3],
            "preco":            row[4],
            "data_criacao":     row[5],
            "data_atualizacao": row[6],
        }
        for row in rows
    ]