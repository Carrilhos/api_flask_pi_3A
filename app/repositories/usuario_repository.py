from app.database import get_connection


def find_all_usuarios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_usuario,
                nome,
                sobrenome,
                email,
                tipo_usuario,
                data_criacao,
                data_atualizacao
        FROM usuarios
        ORDER BY data_criacao DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    usuarios = []

    for row in rows:
        usuarios.append(
            {
                "id_usuario":       row[0],
                "nome":             row[1],
                "sobrenome":        row[2],
                "email":            row[3],
                "tipo_usuario":     row[4],
                "data_criacao":     row[5],
                "data_atualizacao": row[6],
            }
        )

    return usuarios


def find_usuarios_by_tipo(tipo_usuario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_usuario,
                nome,
                sobrenome,
                email,
                tipo_usuario,
                data_criacao,
                data_atualizacao
        FROM usuarios
        WHERE tipo_usuario = %s
        ORDER BY data_criacao DESC
        """,
        (tipo_usuario,),
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    usuarios = []

    for row in rows:
        usuarios.append(
            {
                "id_usuario":       row[0],
                "nome":             row[1],
                "sobrenome":        row[2],
                "email":            row[3],
                "tipo_usuario":     row[4],
                "data_criacao":     row[5],
                "data_atualizacao": row[6],
            }
        )

    return usuarios


def find_usuario_by_id(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_usuario,
                nome,
                sobrenome,
                email,
                tipo_usuario,
                data_criacao,
                data_atualizacao
        FROM usuarios
        WHERE id_usuario = %s
        """,
        (id_usuario,),
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id_usuario":       row[0],
        "nome":             row[1],
        "sobrenome":        row[2],
        "email":            row[3],
        "tipo_usuario":     row[4],
        "data_criacao":     row[5],
        "data_atualizacao": row[6],
    }


def find_usuario_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_usuario,
                nome,
                sobrenome,
                email,
                tipo_usuario,
                data_criacao,
                data_atualizacao,
                senha
        FROM usuarios
        WHERE email = %s
        """,
        (email,),
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id_usuario":       row[0],
        "nome":             row[1],
        "sobrenome":        row[2],
        "email":            row[3],
        "tipo_usuario":     row[4],
        "data_criacao":     row[5],
        "data_atualizacao": row[6],
        "senha":            row[7],
    }


def create_usuario(nome, sobrenome, email, tipo_usuario, senha):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO usuarios (nome, sobrenome, email, tipo_usuario, senha) -- <--- E AQUI
        VALUES (%s, %s, %s, %s, %s) -
        RETURNING id_usuario, nome, sobrenome, email, tipo_usuario, data_criacao, data_atualizacao
        """,
        (nome, sobrenome, email, tipo_usuario, senha),
    )

    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "id_usuario":       row[0],
        "nome":             row[1],
        "sobrenome":        row[2],
        "email":            row[3],
        "tipo_usuario":     row[4],
        "data_criacao":     row[5],
        "data_atualizacao": row[6],
    }


def update_usuario(id_usuario, nome, sobrenome, email, tipo_usuario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE usuarios
        SET nome         = %s,
            sobrenome    = %s,
            email        = %s,
            tipo_usuario = %s
        WHERE id_usuario = %s
        RETURNING id_usuario,
                  nome,
                  sobrenome,
                  email,
                  tipo_usuario,
                  data_criacao,
                  data_atualizacao
        """,
        (nome, sobrenome, email, tipo_usuario, id_usuario),
    )

    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id_usuario":       row[0],
        "nome":             row[1],
        "sobrenome":        row[2],
        "email":            row[3],
        "tipo_usuario":     row[4],
        "data_criacao":     row[5],
        "data_atualizacao": row[6],
    }


def delete_usuario(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM usuarios
        WHERE id_usuario = %s
        RETURNING id_usuario
        """,
        (id_usuario,),
    )

    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return row is not None