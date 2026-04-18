from math import degrees

from flask import Blueprint, jsonify
from app.services.product_service import (
    get_all_produtos,
    get_produto_by_id,
)

produto_bp = Blueprint("produto", __name__)

@produto_bp.route("/produtos", methods=["GET"])
def get_products_old():
    products = get_all_produtos()
    return jsonify(products), 200

@produto_bp.route("/produtos/<int:id_produto>")
def produto_by_id(id_produto):
    produto = get_produto_by_id(id_produto)

    if not produto:
        return {"message": "Produto não encontrado"}, 404

    return jsonify(produto)