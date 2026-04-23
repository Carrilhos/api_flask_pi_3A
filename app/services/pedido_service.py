from app.database import get_connection
from app.repositories.anuncio_repository import buscar_anuncio
from app.repositories.usuario_endereco_repository import buscar_endereco
from app.repositories.pedido_repository import inserir_pedido
from app.repositories.pedido_item_repository import inserir_pedido_item


def criar_pedido(id_usuario, id_endereco, itens):
    conn = get_connection()

    try:
        # ------------------------------------------------------------------
        # 1. Validar estoque de todos os itens
        # ------------------------------------------------------------------
        erros_estoque = []
        anuncios_cache = {}

        for item in itens:
            id_anuncio = item["id_anuncio"]
            quantidade = int(item["quantidade"])

            anuncio = buscar_anuncio(conn, id_anuncio)

            if not anuncio:
                raise ValueError(f"Anúncio {id_anuncio} não encontrado.")

            anuncios_cache[id_anuncio] = anuncio

            estoque = anuncio["estoque"]

            if estoque <= 0:
                erros_estoque.append(
                    f"Anúncio {id_anuncio} ('{anuncio['titulo']}') está sem estoque."
                )
            elif quantidade > estoque:
                erros_estoque.append(
                    f"Anúncio {id_anuncio} ('{anuncio['titulo']}') possui apenas "
                    f"{estoque} unidade(s) em estoque (solicitado: {quantidade})."
                )

        if erros_estoque:
            raise ValueError(erros_estoque)

        # ------------------------------------------------------------------
        # 2. Buscar endereço para snapshot
        # ------------------------------------------------------------------
        endereco = buscar_endereco(conn, id_endereco)

        if not endereco:
            raise ValueError("Endereço não encontrado.")

        # ------------------------------------------------------------------
        # 3. Calcular valor total
        # ------------------------------------------------------------------
        valor_total = sum(
            float(anuncios_cache[item["id_anuncio"]]["preco"]) * int(item["quantidade"])
            for item in itens
        )

        # ------------------------------------------------------------------
        # 4. Criar pedido
        # ------------------------------------------------------------------
        dados_pedido = {
            "id_cliente":       id_usuario,
            "valor_total":      round(valor_total, 2),
            "logradouro_snap":  endereco["logradouro"],
            "numero_snap":      endereco["numero"],
            "bairro_snap":      endereco["bairro"],
            "cidade_snap":      endereco["cidade"],
            "estado_snap":      endereco["estado"],
            "cep_snap":         endereco["cep"],
            "status":           "pendente",
        }

        id_pedido = inserir_pedido(conn, dados_pedido)

        # ------------------------------------------------------------------
        # 5. Criar itens do pedido
        # ------------------------------------------------------------------
        itens_criados = []

        for item in itens:
            id_anuncio = item["id_anuncio"]
            quantidade = int(item["quantidade"])
            preco      = float(anuncios_cache[id_anuncio]["preco"])

            item_criado = inserir_pedido_item(conn, id_pedido, id_anuncio, quantidade, preco)
            itens_criados.append(item_criado)

        # ------------------------------------------------------------------
        # 6. Commit — tudo ou nada
        # ------------------------------------------------------------------
        conn.commit()

        return {
            "id_pedido":        id_pedido,
            "id_cliente":       id_usuario,
            "valor_total":      round(valor_total, 2),
            "logradouro_snap":  endereco["logradouro"],
            "numero_snap":      endereco["numero"],
            "bairro_snap":      endereco["bairro"],
            "cidade_snap":      endereco["cidade"],
            "estado_snap":      endereco["estado"],
            "cep_snap":         endereco["cep"],
            "status":           "pendente",
            "itens":            itens_criados,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()