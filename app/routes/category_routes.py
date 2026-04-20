from flask import Blueprint, jsonify
from app.services.category_service import (
    get_all_categories,
    get_category_by_id
)

category_bp = Blueprint("category", __name__)

@category_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = get_all_categories()
    return jsonify(categories), 200

@category_bp.route("/categories/<int:id_category>", methods=["GET"])
def category_by_id(id_category):
    category = get_category_by_id(id_category)

    if not category:
        return {"message": "Categoria não encontrada"}, 404

    return jsonify(category), 200