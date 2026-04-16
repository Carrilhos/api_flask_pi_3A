from flask import Blueprint, jsonify
from app.services.user_service import get_all_users

user_bp = Blueprint('user', __name__, url_prefix="/api")

@user_bp.route("/")
def home():
    return jsonify({
        "message": "API Flask funcionando"
    })

@user_bp.route("/users", strict_slashes=False)
def get_users():
    users = get_all_users()
    return jsonify(users)