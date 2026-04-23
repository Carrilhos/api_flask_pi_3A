from app.auth import token_required
from flask import Blueprint, request, jsonify
from app.repositories.pedido_repository import (
    find_all_pedidos,
    find_pedidos_by_cliente,
    find_pedido_by_id,
    create_pedido,
    update_pedido,
    update_status_pedido,
    delete_pedido,
)

# ---------------------------------------------------------------------------
# Blueprint
# ---------------------------------------------------------------------------
pedido_bp = Blueprint("pedido", __name__, url_prefix="/pedidos")

# ---------------------------------------------------------------------------
# Status permitidos (conforme constraint da tabela: varchar(9))
# ---------------------------------------------------------------------------
STATUS_VALIDOS = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validar_status(status: str):
    if status not in STATUS_VALIDOS:
        return False, f"Status inválido. Permitidos: {', '.join(STATUS_VALIDOS)}"
    return True, None


def _campos_obrigatorios(data: dict, campos: list):
    faltando = [c for c in campos if c not in data or data[c] is None]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None


# ---------------------------------------------------------------------------
# GET /pedidos  →  lista todos (filtro opcional por id_cliente e status)
# ---------------------------------------------------------------------------
@pedido_bp.route("/", methods=["GET"])
def listar_pedidos():
    try:
        id_cliente = request.args.get("id_cliente", type=int)
        status     = request.args.get("status")

        if status:
            valido, erro = _validar_status(status)
            if not valido:
                return jsonify({"erro": erro}), 400

        if id_cliente:
            pedidos = find_pedidos_by_cliente(id_cliente)
        else:
            pedidos = find_all_pedidos()

        if status:
            pedidos = [p for p in pedidos if p["status"] == status]

        return jsonify(pedidos), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao listar pedidos.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# GET /pedidos/<id>  →  busca um pedido pelo ID
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>", methods=["GET"])
def buscar_pedido(id_pedido: int):
    try:
        pedido = find_pedido_by_id(id_pedido)

        if not pedido:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        return jsonify(pedido), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao buscar pedido.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# POST /pedidos  →  cria um novo pedido
# ---------------------------------------------------------------------------
@pedido_bp.route("/", methods=["POST"])
@token_required
def criar_pedido(current_user_id):
    """
    Body JSON esperado (id_cliente removido, vem do Token):
    {
        "valor_total":     150.00,
        "logradouro_snap": "Rua das Flores",
        "numero_snap":     "123",
        "cidade_snap":     "Porto Alegre",
        "estado_snap":     "RS",
        "cep_snap":        "90000-000",
        "status":          "pendente"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        campos = [
            "valor_total", "logradouro_snap",
            "numero_snap", "cidade_snap", "estado_snap",
            "cep_snap", "status",
        ]
        ok, erro = _campos_obrigatorios(data, campos)
        if not ok:
            return jsonify({"erro": erro}), 400

        ok, erro = _validar_status(data["status"])
        if not ok:
            return jsonify({"erro": erro}), 400

        try:
            valor = float(data["valor_total"])
            if valor < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"erro": "valor_total deve ser um número positivo."}), 400

        pedido = create_pedido(
            id_cliente      = current_user_id,
            valor_total     = round(valor, 2),
            logradouro_snap = str(data["logradouro_snap"])[:255],
            numero_snap     = str(data["numero_snap"])[:10],
            cidade_snap     = str(data["cidade_snap"])[:100],
            estado_snap     = str(data["estado_snap"])[:100],
            cep_snap        = str(data["cep_snap"])[:9],
            status          = data["status"],
        )

        return jsonify(pedido), 201

    except Exception as e:
        return jsonify({"erro": "Erro ao criar pedido.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# PUT /pedidos/<id>  →  atualiza um pedido completo
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>", methods=["PUT"])
def atualizar_pedido(id_pedido: int):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        campos = [
            "valor_total", "logradouro_snap", "numero_snap",
            "cidade_snap", "estado_snap", "cep_snap", "status",
        ]
        ok, erro = _campos_obrigatorios(data, campos)
        if not ok:
            return jsonify({"erro": erro}), 400

        ok, erro = _validar_status(data["status"])
        if not ok:
            return jsonify({"erro": erro}), 400

        try:
            valor = round(float(data["valor_total"]), 2)
            if valor < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"erro": "valor_total deve ser um número positivo."}), 400

        pedido = update_pedido(
            id_pedido       = id_pedido,
            valor_total     = valor,
            logradouro_snap = str(data["logradouro_snap"])[:255],
            numero_snap     = str(data["numero_snap"])[:10],
            cidade_snap     = str(data["cidade_snap"])[:100],
            estado_snap     = str(data["estado_snap"])[:100],
            cep_snap        = str(data["cep_snap"])[:9],
            status          = data["status"],
        )

        if not pedido:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        return jsonify(pedido), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar pedido.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# PATCH /pedidos/<id>/status  →  atualiza apenas o status
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>/status", methods=["PATCH"])
def atualizar_status(id_pedido: int):
    try:
        data = request.get_json()

        if not data or "status" not in data:
            return jsonify({"erro": "Campo 'status' é obrigatório."}), 400

        ok, erro = _validar_status(data["status"])
        if not ok:
            return jsonify({"erro": erro}), 400

        pedido = update_status_pedido(id_pedido, data["status"])

        if not pedido:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        return jsonify(pedido), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar status.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# DELETE /pedidos/<id>  →  remove um pedido
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>", methods=["DELETE"])
def deletar_pedido(id_pedido: int):
    try:
        deletado = delete_pedido(id_pedido)

        if not deletado:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        return jsonify({"mensagem": "Pedido deletado com sucesso."}), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao deletar pedido.", "detalhe": str(e)}), 500