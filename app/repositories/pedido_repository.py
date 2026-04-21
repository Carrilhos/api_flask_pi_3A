from app.database import get_connection


def find_all_pedidos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_pedido,
                id_cliente,
                valor_total,
                logradouro_snap,
                numero_snap,
                cidade_snap,
                estado_snap,
                cep_snap,
                status,
                data_pedido,
                data_criacao,
                data_atualizacao
        FROM pedido
        ORDER BY data_pedido DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    pedidos = []

    for row in rows:
        pedidos.append(
            {
                "id_pedido":        row[0],
                "id_cliente":       row[1],
                "valor_total":      row[2],
                "logradouro_snap":  row[3],
                "numero_snap":      row[4],
                "cidade_snap":      row[5],
                "estado_snap":      row[6],
                "cep_snap":         row[7],
                "status":           row[8],
                "data_pedido":      row[9],
                "data_criacao":     row[10],
                "data_atualizacao": row[11],
            }
        )

    return pedidos


def find_pedidos_by_cliente(id_cliente):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_pedido,
                id_cliente,
                valor_total,
                logradouro_snap,
                numero_snap,
                cidade_snap,
                estado_snap,
                cep_snap,
                status,
                data_pedido,
                data_criacao,
                data_atualizacao
        FROM pedido
        WHERE id_cliente = %s
        ORDER BY data_pedido DESC
        """,
        (id_cliente,),
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    pedidos = []

    for row in rows:
        pedidos.append(
            {
                "id_pedido":        row[0],
                "id_cliente":       row[1],
                "valor_total":      row[2],
                "logradouro_snap":  row[3],
                "numero_snap":      row[4],
                "cidade_snap":      row[5],
                "estado_snap":      row[6],
                "cep_snap":         row[7],
                "status":           row[8],
                "data_pedido":      row[9],
                "data_criacao":     row[10],
                "data_atualizacao": row[11],
            }
        )

    return pedidos


def find_pedido_by_id(id_pedido):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  id_pedido,
                id_cliente,
                valor_total,
                logradouro_snap,
                numero_snap,
                cidade_snap,
                estado_snap,
                cep_snap,
                status,
                data_pedido,
                data_criacao,
                data_atualizacao
        FROM pedido
        WHERE id_pedido = %s
        """,
        (id_pedido,),
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id_pedido":        row[0],
        "id_cliente":       row[1],
        "valor_total":      row[2],
        "logradouro_snap":  row[3],
        "numero_snap":      row[4],
        "cidade_snap":      row[5],
        "estado_snap":      row[6],
        "cep_snap":         row[7],
        "status":           row[8],
        "data_pedido":      row[9],
        "data_criacao":     row[10],
        "data_atualizacao": row[11],
    }


def create_pedido(id_cliente, valor_total, logradouro_snap, numero_snap,
                  cidade_snap, estado_snap, cep_snap, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO pedido (
            id_cliente,
            valor_total,
            logradouro_snap,
            numero_snap,
            cidade_snap,
            estado_snap,
            cep_snap,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_pedido,
                  id_cliente,
                  valor_total,
                  logradouro_snap,
                  numero_snap,
                  cidade_snap,
                  estado_snap,
                  cep_snap,
                  status,
                  data_pedido,
                  data_criacao,
                  data_atualizacao
        """,
        (id_cliente, valor_total, logradouro_snap, numero_snap,
         cidade_snap, estado_snap, cep_snap, status),
    )

    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "id_pedido":        row[0],
        "id_cliente":       row[1],
        "valor_total":      row[2],
        "logradouro_snap":  row[3],
        "numero_snap":      row[4],
        "cidade_snap":      row[5],
        "estado_snap":      row[6],
        "cep_snap":         row[7],
        "status":           row[8],
        "data_pedido":      row[9],
        "data_criacao":     row[10],
        "data_atualizacao": row[11],
    }


def update_pedido(id_pedido, valor_total, logradouro_snap, numero_snap,
                  cidade_snap, estado_snap, cep_snap, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE pedido
        SET valor_total     = %s,
            logradouro_snap = %s,
            numero_snap     = %s,
            cidade_snap     = %s,
            estado_snap     = %s,
            cep_snap        = %s,
            status          = %s
        WHERE id_pedido = %s
        RETURNING id_pedido,
                  id_cliente,
                  valor_total,
                  logradouro_snap,
                  numero_snap,
                  cidade_snap,
                  estado_snap,
                  cep_snap,
                  status,
                  data_pedido,
                  data_criacao,
                  data_atualizacao
        """,
        (valor_total, logradouro_snap, numero_snap,
         cidade_snap, estado_snap, cep_snap, status, id_pedido),
    )

    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id_pedido":        row[0],
        "id_cliente":       row[1],
        "valor_total":      row[2],
        "logradouro_snap":  row[3],
        "numero_snap":      row[4],
        "cidade_snap":      row[5],
        "estado_snap":      row[6],
        "cep_snap":         row[7],
        "status":           row[8],
        "data_pedido":      row[9],
        "data_criacao":     row[10],
        "data_atualizacao": row[11],
    }


def update_status_pedido(id_pedido, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE pedido
        SET status = %s
        WHERE id_pedido = %s
        RETURNING id_pedido,
                  id_cliente,
                  status,
                  data_atualizacao
        """,
        (status, id_pedido),
    )

    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id_pedido":        row[0],
        "id_cliente":       row[1],
        "status":           row[2],
        "data_atualizacao": row[3],
    }


def delete_pedido(id_pedido):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM pedido
        WHERE id_pedido = %s
        RETURNING id_pedido
        """,
        (id_pedido,),
    )

    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return row is not None