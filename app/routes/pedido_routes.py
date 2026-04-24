from app.auth import token_required
from flask import Blueprint, request, jsonify
from app.services.pedido_service import (
  criar_pedido_service,
  cancelar_pedido_service
)
from app.repositories.pedido_repository import (
    find_pedidos_by_cliente,
    find_pedido_by_id,
    update_status_pedido
)

pedido_bp = Blueprint("pedido", __name__, url_prefix="/pedidos")
STATUS_VALIDOS = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}

# ---------------------------------------------------------------------------
# GET /pedidos  →  Lista apenas os pedidos do usuário logado
# ---------------------------------------------------------------------------
@pedido_bp.route("/", methods=["GET"])
@token_required
def listar_pedidos(current_user_id):
    try:
        # Busca apenas os pedidos do dono do token
        pedidos = find_pedidos_by_cliente(current_user_id)
        return jsonify(pedidos), 200
    except Exception as e:
        return jsonify({"erro": "Erro ao listar pedidos.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# GET /pedidos/<id>  →  Busca um pedido específico
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>", methods=["GET"])
@token_required
def buscar_pedido(current_user_id, id_pedido: int):
    try:
        pedido = find_pedido_by_id(id_pedido)
        
        # Verifica se o pedido existe a pertence ao usuário que está buscando
        if not pedido or pedido["id_cliente"] != current_user_id:
            return jsonify({"erro": "Pedido não encontrado ou acesso negado."}), 404
            
        return jsonify(pedido), 200
    except Exception as e:
        return jsonify({"erro": "Erro ao buscar pedido.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# POST /pedidos  →  Cria o pedido usando o Service 
# ---------------------------------------------------------------------------
@pedido_bp.route("/", methods=["POST"])
@token_required
def criar(current_user_id):
    try:
        data = request.get_json()
        if not data or "id_endereco" not in data or "itens" not in data:
            return jsonify({"erro": "O payload deve conter 'id_endereco' e 'itens'."}), 400

        if not isinstance(data["itens"], list) or len(data["itens"]) == 0:
            return jsonify({"erro": "A lista de 'itens' não pode estar vazia."}), 400

        pedido_completo = criar_pedido_service(current_user_id, data["id_endereco"], data["itens"])
        return jsonify(pedido_completo), 201

    except ValueError as e:
        # Tratamento de erros da validações de regra de negócio
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": "Erro interno ao criar pedido.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# DELETE /pedidos/<id>  →  Cancela o pedido (Soft Delete) e estorna estoque
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>", methods=["DELETE"])
@token_required
def cancelar_pedido_rota(current_user_id, id_pedido: int):
    try:
        cancelar_pedido_service(current_user_id, id_pedido)
        return jsonify({"mensagem": "Pedido cancelado com sucesso e estoque devolvido aos anúncios."}), 200
        
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 404 
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400 
    except Exception as e:
        return jsonify({"erro": "Erro ao cancelar pedido.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# PATCH /pedidos/<id>/status  →  Atualização do admin (Oculta dos usuários comuns no futuro)
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>/status", methods=["PATCH"])
def atualizar_status(id_pedido: int):
    # Obs: essa rota talvez fique restrita para admin no futuro.
    # Por enquanto deixei sem token_required pra não quebrar o que já está integrado,
    # mas o ideal depois é colocar algo como @admin_required.
    try:
        data = request.get_json()
        if not data or "status" not in data or data["status"] not in STATUS_VALIDOS:
            return jsonify({"erro": "Status inválido."}), 400

        pedido = update_status_pedido(id_pedido, data["status"])
        if not pedido:
            return jsonify({"erro": "Pedido não encontrado."}), 404
        return jsonify(pedido), 200
    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar status.", "detalhe": str(e)}), 500