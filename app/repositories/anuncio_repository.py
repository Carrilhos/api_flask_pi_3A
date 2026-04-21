from app.database import get_connection


def find_all_anuncios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_anuncio,
                id_vendedor,
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

    anuncios = []

    for row in rows:
        anuncios.append(
            {
                "id_anuncio":       row[0],
                "id_vendedor":      row[1],
                "titulo":           row[2],
                "descricao":        row[3],
                "preco":            row[4],
                "estoque":          row[5],
                "data_criacao":     row[6],
                "data_atualizacao": row[7],
            }
        )

    return anuncios


def find_anuncios_by_vendedor(id_vendedor):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_anuncio,
                id_vendedor,
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

    anuncios = []

    for row in rows:
        anuncios.append(
            {
                "id_anuncio":       row[0],
                "id_vendedor":      row[1],
                "titulo":           row[2],
                "descricao":        row[3],
                "preco":            row[4],
                "estoque":          row[5],
                "data_criacao":     row[6],
                "data_atualizacao": row[7],
            }
        )

    return anuncios


def find_anuncio_by_id(id_anuncio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_anuncio,
                id_vendedor,
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

    return {
        "id_anuncio":       row[0],
        "id_vendedor":      row[1],
        "titulo":           row[2],
        "descricao":        row[3],
        "preco":            row[4],
        "estoque":          row[5],
        "data_criacao":     row[6],
        "data_atualizacao": row[7],
    }


def create_anuncio(id_vendedor, titulo, descricao, preco, estoque):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO anuncio (
            id_vendedor,
            titulo,
            descricao,
            preco,
            estoque
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_anuncio,
                  id_vendedor,
                  titulo,
                  descricao,
                  preco,
                  estoque,
                  data_criacao,
                  data_atualizacao
        """,
        (id_vendedor, titulo, descricao, preco, estoque),
    )

    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "id_anuncio":       row[0],
        "id_vendedor":      row[1],
        "titulo":           row[2],
        "descricao":        row[3],
        "preco":            row[4],
        "estoque":          row[5],
        "data_criacao":     row[6],
        "data_atualizacao": row[7],
    }


def update_anuncio(id_anuncio, titulo, descricao, preco, estoque):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE anuncio
        SET titulo    = %s,
            descricao = %s,
            preco     = %s,
            estoque   = %s
        WHERE id_anuncio = %s
        RETURNING id_anuncio,
                  id_vendedor,
                  titulo,
                  descricao,
                  preco,
                  estoque,
                  data_criacao,
                  data_atualizacao
        """,
        (titulo, descricao, preco, estoque, id_anuncio),
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
        "titulo":           row[2],
        "descricao":        row[3],
        "preco":            row[4],
        "estoque":          row[5],
        "data_criacao":     row[6],
        "data_atualizacao": row[7],
    }


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
        "estoque":          row[2],
        "data_atualizacao": row[3],
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