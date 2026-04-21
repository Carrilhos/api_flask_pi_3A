from app.database import get_connection


def inserir_imagem(
    id_produto,
    id_anuncio,
    url,
    nome_arquivo=None,
    ordem=0,
    principal=False
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO produto_imagem (
            id_produto,
            id_anuncio,
            url,
            nome_arquivo,
            ordem,
            principal
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            id_produto,
            id_anuncio,
            url,
            nome_arquivo,
            ordem,
            principal
        )
    )

    conn.commit()

    cursor.close()
    conn.close()


def find_by_produto(id_produto):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id_imagem,
            url,
            nome_arquivo,
            ordem,
            principal
        FROM produto_imagem
        WHERE id_produto = %s
        ORDER BY ordem
        """,
        (id_produto,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def definir_principal(id_produto, id_imagem):
    conn = get_connection()
    cursor = conn.cursor()

    # remove principal atual
    cursor.execute(
        """
        UPDATE produto_imagem
        SET principal = false
        WHERE id_produto = %s
        """,
        (id_produto,)
    )

    # define nova principal
    cursor.execute(
        """
        UPDATE produto_imagem
        SET principal = true
        WHERE id_imagem = %s
        """,
        (id_imagem,)
    )

    conn.commit()

    cursor.close()
    conn.close()