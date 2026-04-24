from app.database import get_connection

def _agrupar_pedidos_com_itens(rows):
    """Função auxiliar para agrupar as linhas do LEFT JOIN em pedidos únicos com suas listas de itens."""
    pedidos_dict = {}
    for row in rows:
        id_pedido = row[0]
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
                "itens":            []
            }
        
        # row[12] é o id_pedido_item. Se existir, adiciona à lista
        if row[12] is not None:
            pedidos_dict[id_pedido]["itens"].append({
                "id_pedido_item": row[12],
                "id_anuncio":     row[13],
                "quantidade":     row[14],
                "preco":          row[15],
            })
    return list(pedidos_dict.values())


def find_all_pedidos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT  p.id_pedido, p.id_cliente, p.valor_total, p.logradouro_snap, p.numero_snap,
                p.cidade_snap, p.estado_snap, p.cep_snap, p.status, p.data_pedido,
                p.data_criacao, p.data_atualizacao,
                i.id_pedido_item, i.id_anuncio, i.quantidade, i.preco
        FROM pedido p
        LEFT JOIN pedido_item i ON p.id_pedido = i.id_pedido
        ORDER BY p.data_pedido DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return _agrupar_pedidos_com_itens(rows)


def find_pedidos_by_cliente(id_cliente):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT  p.id_pedido, p.id_cliente, p.valor_total, p.logradouro_snap, p.numero_snap,
                p.cidade_snap, p.estado_snap, p.cep_snap, p.status, p.data_pedido,
                p.data_criacao, p.data_atualizacao,
                i.id_pedido_item, i.id_anuncio, i.quantidade, i.preco
        FROM pedido p
        LEFT JOIN pedido_item i ON p.id_pedido = i.id_pedido
        WHERE p.id_cliente = %s
        ORDER BY p.data_pedido DESC
    """, (id_cliente,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return _agrupar_pedidos_com_itens(rows)


def find_pedido_by_id(id_pedido):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT  p.id_pedido, p.id_cliente, p.valor_total, p.logradouro_snap, p.numero_snap,
                p.cidade_snap, p.estado_snap, p.cep_snap, p.status, p.data_pedido,
                p.data_criacao, p.data_atualizacao,
                i.id_pedido_item, i.id_anuncio, i.quantidade, i.preco
        FROM pedido p
        LEFT JOIN pedido_item i ON p.id_pedido = i.id_pedido
        WHERE p.id_pedido = %s
    """, (id_pedido,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    pedidos = _agrupar_pedidos_com_itens(rows)
    return pedidos[0] if pedidos else None


def criar_pedido(id_cliente, valor_total, snaps, itens):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Insere o pedido
        cursor.execute("""
            INSERT INTO pedido (id_cliente, valor_total, logradouro_snap, numero_snap, cidade_snap, estado_snap, cep_snap, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendente')
            RETURNING id_pedido
        """, (id_cliente, valor_total, snaps['logradouro_snap'], snaps['numero_snap'], snaps['cidade_snap'], snaps['estado_snap'], snaps['cep_snap']))
        
        id_pedido = cursor.fetchone()[0]

        # Insere os itens e desconta do estoque
        for item in itens:
            # Insere em pedido_item
            cursor.execute("""
                INSERT INTO pedido_item (id_pedido, id_anuncio, quantidade, preco)
                VALUES (%s, %s, %s, %s)
            """, (id_pedido, item['id_anuncio'], item['quantidade'], item['preco']))
            
            # Baixa o estoque
            cursor.execute("""
                UPDATE anuncio SET estoque = estoque - %s WHERE id_anuncio = %s
            """, (item['quantidade'], item['id_anuncio']))

        conn.commit() # Salva tudo junto
        return find_pedido_by_id(id_pedido) # Retorna o pedido completo formatado

    except Exception as e:
        conn.rollback() # Se deu erro, cancela tudo para não sujar o banco
        raise e
    finally:
        cursor.close()
        conn.close()

def update_status_pedido(id_pedido, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE pedido SET status = %s WHERE id_pedido = %s
        RETURNING id_pedido, id_cliente, status, data_atualizacao
    """, (status, id_pedido))
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    
    if not row: return None
    return {"id_pedido": row[0], "id_cliente": row[1], "status": row[2], "data_atualizacao": row[3]}

def cancelar_pedido(id_pedido):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Muda o status do pedido para cancelado
        cursor.execute("""
            UPDATE pedido 
            SET status = 'cancelado', data_atualizacao = NOW()
            WHERE id_pedido = %s
        """, (id_pedido,))

        # Busca os itens desse pedido para saber o que devolver
        cursor.execute("""
            SELECT id_anuncio, quantidade 
            FROM pedido_item 
            WHERE id_pedido = %s
        """, (id_pedido,))
        itens = cursor.fetchall()

        # Devolve a quantidade para o estoque de cada anúncio
        for item in itens:
            id_anuncio = item[0]
            quantidade = item[1]
            
            cursor.execute("""
                UPDATE anuncio 
                SET estoque = estoque + %s 
                WHERE id_anuncio = %s
            """, (quantidade, id_anuncio))

        conn.commit() # Salva o cancelamento e o estorno juntos
        return True

    except Exception as e:
        conn.rollback() # Se der erro, desfaz tudo
        raise e
    finally:
        cursor.close()
        conn.close()