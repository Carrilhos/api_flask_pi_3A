from flask import Blueprint, jsonify
from app.services.product_service import (
    get_all_produtos,
    get_produto_by_id
)

produto_bp = Blueprint("produto", __name__)


@produto_bp.route("/produtos")
def produtos():
    return jsonify(get_all_produtos())


@produto_bp.route("/produtos/<int:id_produto>")
def produto_by_id(id_produto):
    produto = get_produto_by_id(id_produto)

    if not produto:
        return {"message": "Produto não encontrado"}, 404

    return jsonify(produto)