from flask import Blueprint, request, jsonify
from app.services.pedido_service import criar_pedido
from app.repositories.pedido_repository import (
    find_all_pedidos,
    find_pedidos_by_cliente,
    find_pedido_by_id,
    update_pedido,
    update_status_pedido,
    delete_pedido,
)

pedido_bp = Blueprint("pedido", __name__, url_prefix="/pedidos")

STATUS_VALIDOS = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}


def _campos_obrigatorios(data: dict, campos: list):
    faltando = [c for c in campos if c not in data or data[c] is None]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None


def _validar_status(status: str):
    if status not in STATUS_VALIDOS:
        return False, f"Status inválido. Permitidos: {', '.join(STATUS_VALIDOS)}"
    return True, None


# ---------------------------------------------------------------------------
# GET /pedidos
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

        pedidos = find_pedidos_by_cliente(id_cliente) if id_cliente else find_all_pedidos()

        if status:
            pedidos = [p for p in pedidos if p["status"] == status]

        return jsonify(pedidos), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao listar pedidos.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# GET /pedidos/<id>
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
# POST /pedidos  →  finaliza carrinho
# ---------------------------------------------------------------------------
@pedido_bp.route("/", methods=["POST"])
def criar():
    data = request.get_json()

    if not data:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

    ok, erro = _campos_obrigatorios(data, ["id_usuario", "id_endereco", "itens"])
    if not ok:
        return jsonify({"erro": erro}), 400

    if not isinstance(data["itens"], list) or len(data["itens"]) == 0:
        return jsonify({"erro": "itens deve ser uma lista com ao menos um item."}), 400

    for i, item in enumerate(data["itens"]):
        if "id_anuncio" not in item or "quantidade" not in item:
            return jsonify({
                "erro": f"Item {i + 1} inválido. Cada item precisa de 'id_anuncio' e 'quantidade'."
            }), 400

        try:
            if int(item["quantidade"]) <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                "erro": f"Item {i + 1}: 'quantidade' deve ser um número inteiro positivo."
            }), 400

    try:
        pedido = criar_pedido(
            id_usuario  = data["id_usuario"],
            id_endereco = data["id_endereco"],
            itens       = data["itens"],
        )
        return jsonify(pedido), 201

    except ValueError as e:
        erro = e.args[0]
        if isinstance(erro, list):
            return jsonify({"erro": "Estoque insuficiente.", "detalhes": erro}), 400
        return jsonify({"erro": str(erro)}), 400

    except Exception as e:
        return jsonify({"erro": "Erro ao criar pedido.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# PUT /pedidos/<id>
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
# PATCH /pedidos/<id>/status
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
# DELETE /pedidos/<id>
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