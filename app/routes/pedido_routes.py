from flask import Blueprint, request, jsonify
from supabase import create_client, Client
from datetime import datetime
import os

# ---------------------------------------------------------------------------
# Configuração do Supabase
# ---------------------------------------------------------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")  # use a service_role key no backend

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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


def _campos_obrigatorios(data: dict, campos: list[str]):
    faltando = [c for c in campos if c not in data or data[c] is None]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None


# ---------------------------------------------------------------------------
# GET /pedidos  →  lista todos (com filtros opcionais por query string)
# ---------------------------------------------------------------------------
@pedido_bp.route("/", methods=["GET"])
def listar_pedidos():
    """
    Query params opcionais:
      - id_cliente (int)
      - status    (str)
      - page      (int, default 1)
      - per_page  (int, default 20)
    """
    try:
        id_cliente = request.args.get("id_cliente", type=int)
        status     = request.args.get("status")
        page       = request.args.get("page", 1, type=int)
        per_page   = request.args.get("per_page", 20, type=int)

        offset = (page - 1) * per_page

        query = supabase.table("pedido").select("*")

        if id_cliente:
            query = query.eq("id_cliente", id_cliente)

        if status:
            valido, erro = _validar_status(status)
            if not valido:
                return jsonify({"erro": erro}), 400
            query = query.eq("status", status)

        response = (
            query
            .order("data_pedido", desc=True)
            .range(offset, offset + per_page - 1)
            .execute()
        )

        return jsonify({
            "page":     page,
            "per_page": per_page,
            "total":    len(response.data),
            "dados":    response.data,
        }), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao listar pedidos.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# GET /pedidos/<id>  →  busca um pedido pelo ID
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>", methods=["GET"])
def buscar_pedido(id_pedido: int):
    try:
        response = (
            supabase.table("pedido")
            .select("*")
            .eq("id_pedido", id_pedido)
            .single()
            .execute()
        )

        if not response.data:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"erro": "Pedido não encontrado.", "detalhe": str(e)}), 404


# ---------------------------------------------------------------------------
# POST /pedidos  →  cria um novo pedido
# ---------------------------------------------------------------------------
@pedido_bp.route("/", methods=["POST"])
def criar_pedido():
    """
    Body JSON esperado:
    {
        "id_cliente":      1,
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

        # Validação de campos obrigatórios
        campos = [
            "id_cliente", "valor_total", "logradouro_snap",
            "numero_snap", "cidade_snap", "estado_snap",
            "cep_snap", "status",
        ]
        ok, erro = _campos_obrigatorios(data, campos)
        if not ok:
            return jsonify({"erro": erro}), 400

        # Validação de status
        ok, erro = _validar_status(data["status"])
        if not ok:
            return jsonify({"erro": erro}), 400

        # Validação de valor_total
        try:
            valor = float(data["valor_total"])
            if valor < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"erro": "valor_total deve ser um número positivo."}), 400

        novo_pedido = {
            "id_cliente":      data["id_cliente"],
            "valor_total":     round(valor, 2),
            "logradouro_snap": str(data["logradouro_snap"])[:255],
            "numero_snap":     str(data["numero_snap"])[:10],
            "cidade_snap":     str(data["cidade_snap"])[:100],
            "estado_snap":     str(data["estado_snap"])[:100],
            "cep_snap":        str(data["cep_snap"])[:9],
            "status":          data["status"],
        }

        response = supabase.table("pedido").insert(novo_pedido).execute()

        return jsonify({
            "mensagem": "Pedido criado com sucesso.",
            "pedido":   response.data[0],
        }), 201

    except Exception as e:
        return jsonify({"erro": "Erro ao criar pedido.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# PUT /pedidos/<id>  →  atualiza um pedido completo
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>", methods=["PUT"])
def atualizar_pedido(id_pedido: int):
    """Atualização completa do pedido (todos os campos editáveis)."""
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

        payload = {
            "valor_total":     round(float(data["valor_total"]), 2),
            "logradouro_snap": str(data["logradouro_snap"])[:255],
            "numero_snap":     str(data["numero_snap"])[:10],
            "cidade_snap":     str(data["cidade_snap"])[:100],
            "estado_snap":     str(data["estado_snap"])[:100],
            "cep_snap":        str(data["cep_snap"])[:9],
            "status":          data["status"],
            "data_atualizacao": datetime.utcnow().isoformat(),
        }

        response = (
            supabase.table("pedido")
            .update(payload)
            .eq("id_pedido", id_pedido)
            .execute()
        )

        if not response.data:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        return jsonify({
            "mensagem": "Pedido atualizado com sucesso.",
            "pedido":   response.data[0],
        }), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar pedido.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# PATCH /pedidos/<id>/status  →  atualiza apenas o status
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>/status", methods=["PATCH"])
def atualizar_status(id_pedido: int):
    """
    Body JSON esperado:
    { "status": "aprovado" }
    """
    try:
        data = request.get_json()
        if not data or "status" not in data:
            return jsonify({"erro": "Campo 'status' é obrigatório."}), 400

        ok, erro = _validar_status(data["status"])
        if not ok:
            return jsonify({"erro": erro}), 400

        response = (
            supabase.table("pedido")
            .update({
                "status": data["status"],
                "data_atualizacao": datetime.utcnow().isoformat(),
            })
            .eq("id_pedido", id_pedido)
            .execute()
        )

        if not response.data:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        return jsonify({
            "mensagem": f"Status atualizado para '{data['status']}'.",
            "pedido":   response.data[0],
        }), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar status.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# DELETE /pedidos/<id>  →  remove um pedido
# ---------------------------------------------------------------------------
@pedido_bp.route("/<int:id_pedido>", methods=["DELETE"])
def deletar_pedido(id_pedido: int):
    try:
        response = (
            supabase.table("pedido")
            .delete()
            .eq("id_pedido", id_pedido)
            .execute()
        )

        if not response.data:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        return jsonify({"mensagem": "Pedido deletado com sucesso."}), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao deletar pedido.", "detalhe": str(e)}), 500