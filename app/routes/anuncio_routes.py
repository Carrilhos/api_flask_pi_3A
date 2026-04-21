from flask import Blueprint, request, jsonify
from app.repositories.anuncio_repository import (
    find_all_anuncios,
    find_anuncios_by_vendedor,
    find_anuncio_by_id,
    create_anuncio,
    update_anuncio,
    update_estoque_anuncio,
    delete_anuncio,
)

# ---------------------------------------------------------------------------
# Blueprint
# ---------------------------------------------------------------------------
anuncio_bp = Blueprint("anuncio", __name__, url_prefix="/anuncios")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _campos_obrigatorios(data: dict, campos: list):
    faltando = [c for c in campos if c not in data or data[c] is None]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None


# ---------------------------------------------------------------------------
# GET /anuncios  →  lista todos (com filtros opcionais por query string)
# ---------------------------------------------------------------------------
@anuncio_bp.route("/", methods=["GET"])
def listar_anuncios():
    """
    Query params opcionais:
      - id_vendedor (int)
      - page        (int, default 1)
      - per_page    (int, default 20)
    """
    try:
        id_vendedor = request.args.get("id_vendedor", type=int)
        page        = request.args.get("page", 1, type=int)
        per_page    = request.args.get("per_page", 20, type=int)

        if id_vendedor:
            anuncios = find_anuncios_by_vendedor(id_vendedor)
        else:
            anuncios = find_all_anuncios()

        # paginação em memória (mover para o repository se a tabela crescer)
        offset   = (page - 1) * per_page
        pagina   = anuncios[offset: offset + per_page]

        return jsonify({
            "page":     page,
            "per_page": per_page,
            "total":    len(anuncios),
            "dados":    pagina,
        }), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao listar anúncios.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# GET /anuncios/<id>  →  busca um anúncio pelo ID
# ---------------------------------------------------------------------------
@anuncio_bp.route("/<int:id_anuncio>", methods=["GET"])
def buscar_anuncio(id_anuncio: int):
    try:
        anuncio = find_anuncio_by_id(id_anuncio)

        if not anuncio:
            return jsonify({"erro": "Anúncio não encontrado."}), 404

        return jsonify(anuncio), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao buscar anúncio.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# POST /anuncios  →  cria um novo anúncio
# ---------------------------------------------------------------------------
@anuncio_bp.route("/", methods=["POST"])
def criar_anuncio():
    """
    Body JSON esperado:
    {
        "id_vendedor": 1,
        "titulo":      "Notebook Dell Inspiron",
        "descricao":   "Seminovo, 16GB RAM",   (opcional)
        "preco":       2500.00,
        "estoque":     5                        (opcional, default 0)
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        ok, erro = _campos_obrigatorios(data, ["id_vendedor", "titulo", "preco"])
        if not ok:
            return jsonify({"erro": erro}), 400

        # Validação de preco
        try:
            preco = float(data["preco"])
            if preco < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"erro": "preco deve ser um número positivo."}), 400

        # Validação de estoque
        estoque = data.get("estoque", 0)
        try:
            estoque = int(estoque)
            if estoque < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"erro": "estoque deve ser um número inteiro não negativo."}), 400

        anuncio = create_anuncio(
            id_vendedor = data["id_vendedor"],
            titulo      = str(data["titulo"])[:255],
            descricao   = data.get("descricao"),
            preco       = round(preco, 2),
            estoque     = estoque,
        )

        return jsonify({
            "mensagem": "Anúncio criado com sucesso.",
            "anuncio":  anuncio,
        }), 201

    except Exception as e:
        return jsonify({"erro": "Erro ao criar anúncio.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# PUT /anuncios/<id>  →  atualiza um anúncio completo
# ---------------------------------------------------------------------------
@anuncio_bp.route("/<int:id_anuncio>", methods=["PUT"])
def atualizar_anuncio(id_anuncio: int):
    """
    Body JSON esperado:
    {
        "titulo":    "Novo título",
        "descricao": "Nova descrição",
        "preco":     1999.90,
        "estoque":   10
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        ok, erro = _campos_obrigatorios(data, ["titulo", "preco"])
        if not ok:
            return jsonify({"erro": erro}), 400

        try:
            preco = round(float(data["preco"]), 2)
            if preco < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"erro": "preco deve ser um número positivo."}), 400

        estoque = data.get("estoque", 0)
        try:
            estoque = int(estoque)
            if estoque < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"erro": "estoque deve ser um número inteiro não negativo."}), 400

        anuncio = update_anuncio(
            id_anuncio = id_anuncio,
            titulo     = str(data["titulo"])[:255],
            descricao  = data.get("descricao"),
            preco      = preco,
            estoque    = estoque,
        )

        if not anuncio:
            return jsonify({"erro": "Anúncio não encontrado."}), 404

        return jsonify({
            "mensagem": "Anúncio atualizado com sucesso.",
            "anuncio":  anuncio,
        }), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar anúncio.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# PATCH /anuncios/<id>/estoque  →  atualiza apenas o estoque
# ---------------------------------------------------------------------------
@anuncio_bp.route("/<int:id_anuncio>/estoque", methods=["PATCH"])
def atualizar_estoque(id_anuncio: int):
    """
    Body JSON esperado:
    { "estoque": 15 }
    """
    try:
        data = request.get_json()

        if not data or "estoque" not in data:
            return jsonify({"erro": "Campo 'estoque' é obrigatório."}), 400

        try:
            estoque = int(data["estoque"])
            if estoque < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"erro": "estoque deve ser um número inteiro não negativo."}), 400

        anuncio = update_estoque_anuncio(id_anuncio, estoque)

        if not anuncio:
            return jsonify({"erro": "Anúncio não encontrado."}), 404

        return jsonify({
            "mensagem": f"Estoque atualizado para {estoque}.",
            "anuncio":  anuncio,
        }), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar estoque.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# DELETE /anuncios/<id>  →  remove um anúncio
# ---------------------------------------------------------------------------
@anuncio_bp.route("/<int:id_anuncio>", methods=["DELETE"])
def deletar_anuncio(id_anuncio: int):
    try:
        deletado = delete_anuncio(id_anuncio)

        if not deletado:
            return jsonify({"erro": "Anúncio não encontrado."}), 404

        return jsonify({"mensagem": "Anúncio deletado com sucesso."}), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao deletar anúncio.", "detalhe": str(e)}), 500