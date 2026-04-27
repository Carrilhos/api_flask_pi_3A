from flask import Blueprint, jsonify
from app.services.category_service import (
    get_all_categories,
    get_category_by_id
)

# ---------------------------------------------------------------------------
# Blueprint - Padronizado para /categorias
# ---------------------------------------------------------------------------
category_bp = Blueprint("category", __name__, url_prefix="/categorias")

# ---------------------------------------------------------------------------
# GET /categorias → lista todas as categorias
# ---------------------------------------------------------------------------
@category_bp.route("/", methods=["GET"])
def listar_categorias():
    """Lista todas as categorias de produtos disponíveis."""
    try:
        categorias = get_all_categories()
        return jsonify(categorias), 200
    except Exception as e:
        return jsonify({"erro": "Erro ao listar categorias.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# GET /categorias/<id> → busca uma categoria pelo ID
# ---------------------------------------------------------------------------
@category_bp.route("/<int:id_categoria>", methods=["GET"])
def buscar_categoria_por_id(id_categoria):
    """Busca os detalhes de uma categoria específica pelo seu ID."""
    try:
        categoria = get_category_by_id(id_categoria)

        if not categoria:
            return jsonify({"erro": "Categoria não encontrada."}), 404

        return jsonify(categoria), 200
    except Exception as e:
        return jsonify({"erro": "Erro ao buscar categoria.", "detalhe": str(e)}), 500