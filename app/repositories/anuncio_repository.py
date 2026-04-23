from app.database import get_connection


def buscar_anuncio(conn, id_anuncio):
    """Usado pelo service — recebe conn aberta para participar da transação."""
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_anuncio,
                id_vendedor,
                id_produto,
                titulo,
                descricao,
                preco,
                estoque,
                data_criacao,
                data_atualizacao
        FROM anuncio
        WHERE id_anuncio = %s
        """,
        (id_anuncio,),
    )

    row = cursor.fetchone()
    cursor.close()

    if not row:
        return None

    return {
        "id_anuncio":       row[0],
        "id_vendedor":      row[1],
        "id_produto":       row[2],
        "titulo":           row[3],
        "descricao":        row[4],
        "preco":            row[5],
        "estoque":          row[6],
        "data_criacao":     row[7],
        "data_atualizacao": row[8],
    }


def find_all_anuncios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_anuncio,
                id_vendedor,
                id_produto,
                titulo,
                descricao,
                preco,
                estoque,
                data_criacao,
                data_atualizacao
        FROM anuncio
        ORDER BY data_criacao DESC
        """
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [_row_to_dict(row) for row in rows]


def find_anuncios_by_vendedor(id_vendedor):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_anuncio,
                id_vendedor,
                id_produto,
                titulo,
                descricao,
                preco,
                estoque,
                data_criacao,
                data_atualizacao
        FROM anuncio
        WHERE id_vendedor = %s
        ORDER BY data_criacao DESC
        """,
        (id_vendedor,),
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [_row_to_dict(row) for row in rows]


def find_anuncio_by_id(id_anuncio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_anuncio,
                id_vendedor,
                id_produto,
                titulo,
                descricao,
                preco,
                estoque,
                data_criacao,
                data_atualizacao
        FROM anuncio
        WHERE id_anuncio = %s
        """,
        (id_anuncio,),
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    return _row_to_dict(row)


def create_anuncio(id_vendedor, id_produto, titulo, descricao, preco, estoque):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO anuncio (
            id_vendedor,
            id_produto,
            titulo,
            descricao,
            preco,
            estoque
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_anuncio,
                  id_vendedor,
                  id_produto,
                  titulo,
                  descricao,
                  preco,
                  estoque,
                  data_criacao,
                  data_atualizacao
        """,
        (id_vendedor, id_produto, titulo, descricao, preco, estoque),
    )

    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return _row_to_dict(row)


def update_anuncio(id_anuncio, id_produto, titulo, descricao, preco, estoque):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE anuncio
        SET id_produto = %s,
            titulo     = %s,
            descricao  = %s,
            preco      = %s,
            estoque    = %s
        WHERE id_anuncio = %s
        RETURNING id_anuncio,
                  id_vendedor,
                  id_produto,
                  titulo,
                  descricao,
                  preco,
                  estoque,
                  data_criacao,
                  data_atualizacao
        """,
        (id_produto, titulo, descricao, preco, estoque, id_anuncio),
    )

    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if not row:
        return None

    return _row_to_dict(row)


def update_estoque_anuncio(id_anuncio, estoque):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE anuncio
        SET estoque = %s
        WHERE id_anuncio = %s
        RETURNING id_anuncio,
                  id_vendedor,
                  id_produto,
                  estoque,
                  data_atualizacao
        """,
        (estoque, id_anuncio),
    )

    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id_anuncio":       row[0],
        "id_vendedor":      row[1],
        "id_produto":       row[2],
        "estoque":          row[3],
        "data_atualizacao": row[4],
    }


def delete_anuncio(id_anuncio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM anuncio
        WHERE id_anuncio = %s
        RETURNING id_anuncio
        """,
        (id_anuncio,),
    )

    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return row is not None

def get_dados_basicos_anuncio_produto(id_anuncio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.id_anuncio, a.titulo, a.descricao, a.preco, a.estoque,
            p.id_produto, p.nome as produto_nome, p.marca, p.modelo, p.fabricante, p.id_categoria
        FROM anuncio a
        LEFT JOIN produto p ON a.id_produto = p.id_produto
        WHERE a.id_anuncio = %s
    """, (id_anuncio,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def get_imagens_por_anuncio(id_anuncio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT url, principal FROM produto_imagem WHERE id_anuncio = %s", (id_anuncio,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_atributos_por_produto(id_produto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT attr.nome, pa.valor_string, pa.valor_number, pa.valor_boolean
        FROM produto_atributo pa
        JOIN atributo attr ON pa.id_atributo = attr.id_atributo
        WHERE pa.id_produto = %s
    """, (id_produto,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def _row_to_dict(row):
    return {
        "id_anuncio":       row[0],
        "id_vendedor":      row[1],
        "id_produto":       row[2],
        "titulo":           row[3],
        "descricao":        row[4],
        "preco":            row[5],
        "estoque":          row[6],
        "data_criacao":     row[7],
        "data_atualizacao": row[8],
    }
