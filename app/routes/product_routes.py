from flask import Blueprint, jsonify
from app.services.product_service import (
    get_all_produtos,
    get_produto_by_id,
)

# ---------------------------------------------------------------------------
# Blueprint - Padronizado para /produtos
# ---------------------------------------------------------------------------
produto_bp = Blueprint("produto", __name__, url_prefix="/produtos")

# ---------------------------------------------------------------------------
# GET /produtos → lista todos os produtos
# ---------------------------------------------------------------------------
@produto_bp.route("/", methods=["GET"])
def listar_produtos():
    """Lista todos os produtos disponíveis."""
    try:
        produtos = get_all_produtos()
        return jsonify(produtos), 200
    except Exception as e:
        return jsonify({
            "erro": "Erro ao listar produtos.",
            "detalhe": str(e)
        }), 500

# ---------------------------------------------------------------------------
# GET /produtos/<id> → busca um produto pelo ID
# ---------------------------------------------------------------------------
@produto_bp.route("/<int:id_produto>", methods=["GET"])
def buscar_produto_por_id(id_produto: int):
    """Busca os detalhes de um produto específico pelo seu ID."""
    try:
        produto = get_produto_by_id(id_produto)

        if not produto:
            return jsonify({"erro": "Produto não encontrado."}), 404

        return jsonify(produto), 200
    except Exception as e:
        return jsonify({
            "erro": "Erro ao buscar produto.",
            "detalhe": str(e)
        }), 500