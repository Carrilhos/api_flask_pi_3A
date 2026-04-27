from app.database import get_connection

def create_endereco(id_usuario, logradouro, numero, bairro, cidade, estado, cep):
    """Insere um novo endereço vinculado a um usuário."""
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
    """Atualiza as informações de um endereço existente."""
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
    """Remove um endereço do banco de dados pelo seu ID."""
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

def find_enderecos_by_usuario(id_usuario):
    """Busca todos os endereços pertencentes a um determinado usuário."""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute(
        """
        SELECT  id_endereco,
                id_usuario,
                logradouro,
                numero,
                bairro,
                cidade,
                estado,
                cep,
                data_criacao,
                data_atualizacao
        FROM usuario_endereco
        WHERE id_usuario = %s
        ORDER BY data_criacao DESC
        """,
        (id_usuario,)
    )
 
    rows = cursor.fetchall()
 
    cursor.close()
    conn.close()
 
    return [_row_to_dict(row) for row in rows]
 
 
def find_endereco_by_id(id_endereco):
    """Busca um endereço específico pelo seu ID."""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute(
        """
        SELECT  id_endereco,
                id_usuario,
                logradouro,
                numero,
                bairro,
                cidade,
                estado,
                cep,
                data_criacao,
                data_atualizacao
        FROM usuario_endereco
        WHERE id_endereco = %s
        """,
        (id_endereco,)
    )
 
    row = cursor.fetchone()
 
    cursor.close()
    conn.close()
 
    if not row:
        return None
 
    return _row_to_dict(row)
 
 
def _row_to_dict(row):
    """Função auxiliar para mapear a tupla retornada do banco em um dicionário de endereço."""
    return {
        "id_endereco":      row[0],
        "id_usuario":       row[1],
        "logradouro":       row[2],
        "numero":           row[3],
        "bairro":           row[4],
        "cidade":           row[5],
        "estado":           row[6],
        "cep":              row[7],
        "data_criacao":     row[8],
        "data_atualizacao": row[9],
    }