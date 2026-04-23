from app.database import get_connection

def create_endereco(id_usuario, logradouro, numero, bairro, cidade, estado, cep):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO usuario_endereco 
        (id_usuario, logradouro, numero, bairro, cidade, estado, cep)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_endereco, id_usuario, logradouro, numero, bairro, cidade, estado, cep, data_criacao, data_atualizacao
        """,
        (id_usuario, logradouro, numero, bairro, cidade, estado, cep)
    )

    row = cursor.fetchone()
    conn.commit()  
    
    cursor.close()
    conn.close()

    return {
        "id_endereco": row[0],
        "id_usuario": row[1],
        "logradouro": row[2],
        "numero": row[3],
        "bairro": row[4],
        "cidade": row[5],
        "estado": row[6],
        "cep": row[7],
        "data_criacao": row[8],
        "data_atualizacao": row[9]
    }


def update_endereco(id_endereco, logradouro, numero, bairro, cidade, estado, cep):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE usuario_endereco 
        SET logradouro = %s, numero = %s, bairro = %s, cidade = %s, estado = %s, cep = %s, data_atualizacao = NOW()
        WHERE id_endereco = %s
        RETURNING id_endereco, id_usuario, logradouro, numero, bairro, cidade, estado, cep, data_criacao, data_atualizacao
        """,
        (logradouro, numero, bairro, cidade, estado, cep, id_endereco)
    )

    row = cursor.fetchone()
    conn.commit()
    
    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id_endereco": row[0],
        "id_usuario": row[1],
        "logradouro": row[2],
        "numero": row[3],
        "bairro": row[4],
        "cidade": row[5],
        "estado": row[6],
        "cep": row[7],
        "data_criacao": row[8],
        "data_atualizacao": row[9]
    }


def delete_endereco(id_endereco):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM usuario_endereco 
        WHERE id_endereco = %s
        RETURNING id_endereco
        """,
        (id_endereco,)
    )

    row = cursor.fetchone()
    conn.commit()
    
    cursor.close()
    conn.close()

    return row is not None  # Retorna True se deletou, False se não achou