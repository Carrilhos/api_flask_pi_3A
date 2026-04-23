from app.database import get_connection


def inserir_pedido(conn, dados):
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO pedido (
            id_cliente,
            valor_total,
            logradouro_snap,
            numero_snap,
            bairro_snap,
            cidade_snap,
            estado_snap,
            cep_snap,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_pedido
        """,
        (
            dados["id_cliente"],
            dados["valor_total"],
            dados["logradouro_snap"],
            dados["numero_snap"],
            dados["bairro_snap"],
            dados["cidade_snap"],
            dados["estado_snap"],
            dados["cep_snap"],
            dados["status"],
        ),
    )

    id_pedido = cursor.fetchone()[0]
    cursor.close()

    return id_pedido


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
                bairro_snap,
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

    return [_row_to_dict(row) for row in rows]


def find_pedidos_by_cliente(id_cliente):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  p.id_pedido,
                p.id_cliente,
                p.valor_total,
                p.logradouro_snap,
                p.numero_snap,
                p.cidade_snap,
                p.estado_snap,
                p.cep_snap,
                p.status,
                p.data_pedido,
                p.data_criacao,
                p.data_atualizacao,
                i.id_pedido_item,
                i.id_anuncio,
                i.quantidade,
                i.preco
        FROM pedido p
        LEFT JOIN pedido_item i ON p.id_pedido = i.id_pedido
        WHERE p.id_cliente = %s
        ORDER BY p.data_pedido DESC
        """,
        (id_cliente,),
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    pedidos_dict = {}

    for row in rows:
        id_pedido = row[0]

        # Cria o pedido no dicionário se ele ainda não existir
        if id_pedido not in pedidos_dict:
            pedidos_dict[id_pedido] = {
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
                "itens":            []  # Lista vazia pronta para receber os itens
            }

        # Se existir um pedido_item atrelado, adiciona na lista
        if row[12] is not None:
            pedidos_dict[id_pedido]["itens"].append({
                "id_pedido_item": row[12],
                "id_anuncio":     row[13],
                "quantidade":     row[14],
                "preco":          row[15],
            })
            
    # Retorna os valores do dicionário como uma lista padrão
    return list(pedidos_dict.values())
    
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
                bairro_snap,
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

    return _row_to_dict(row)


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
                  bairro_snap,
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

    return _row_to_dict(row)


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


def _row_to_dict(row):
    return {
        "id_pedido":        row[0],
        "id_cliente":       row[1],
        "valor_total":      row[2],
        "logradouro_snap":  row[3],
        "numero_snap":      row[4],
        "bairro_snap":      row[5],
        "cidade_snap":      row[6],
        "estado_snap":      row[7],
        "cep_snap":         row[8],
        "status":           row[9],
        "data_pedido":      row[10],
        "data_criacao":     row[11],
        "data_atualizacao": row[12],
    }