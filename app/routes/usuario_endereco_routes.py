from flask import Blueprint, request, jsonify
from app.repositories.usuario_endereco_repository import (
    find_all_enderecos,
    find_enderecos_by_usuario,
    find_endereco_by_id,
    create_endereco,
    update_endereco,
    delete_endereco,
)

endereco_bp = Blueprint("endereco", __name__, url_prefix="/enderecos")


def _campos_obrigatorios(data: dict, campos: list):
    faltando = [c for c in campos if c not in data or data[c] is None]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None


# ---------------------------------------------------------------------------
# GET /enderecos  →  lista todos (filtro opcional por id_usuario)
# ---------------------------------------------------------------------------
@endereco_bp.route("/", methods=["GET"])
def listar_enderecos():
    try:
        id_usuario = request.args.get("id_usuario", type=int)

        if id_usuario:
            enderecos = find_enderecos_by_usuario(id_usuario)
        else:
            enderecos = find_all_enderecos()

        return jsonify(enderecos), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao listar endereços.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# GET /enderecos/<id>
# ---------------------------------------------------------------------------
@endereco_bp.route("/<int:id_endereco>", methods=["GET"])
def buscar_endereco(id_endereco: int):
    try:
        endereco = find_endereco_by_id(id_endereco)

        if not endereco:
            return jsonify({"erro": "Endereço não encontrado."}), 404

        return jsonify(endereco), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao buscar endereço.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# POST /enderecos
# ---------------------------------------------------------------------------
@endereco_bp.route("/", methods=["POST"])
def criar_endereco():
    """
    Body JSON esperado:
    {
        "id_usuario":  1,
        "logradouro": "Rua das Flores",
        "numero":     "123",
        "bairro":     "Centro",
        "cidade":     "Porto Alegre",
        "estado":     "RS",
        "cep":        "90000-000"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        campos = ["id_usuario", "logradouro", "numero", "bairro", "cidade", "estado", "cep"]
        ok, erro = _campos_obrigatorios(data, campos)
        if not ok:
            return jsonify({"erro": erro}), 400

        if len(str(data["estado"])) != 2:
            return jsonify({"erro": "estado deve ter exatamente 2 caracteres (ex: RS)."}), 400

        endereco = create_endereco(
            id_usuario = data["id_usuario"],
            logradouro = str(data["logradouro"])[:255],
            numero     = str(data["numero"])[:10],
            bairro     = str(data["bairro"])[:100],
            cidade     = str(data["cidade"])[:100],
            estado     = str(data["estado"]).upper()[:2],
            cep        = str(data["cep"])[:9],
        )

        return jsonify(endereco), 201

    except Exception as e:
        return jsonify({"erro": "Erro ao criar endereço.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# PUT /enderecos/<id>
# ---------------------------------------------------------------------------
@endereco_bp.route("/<int:id_endereco>", methods=["PUT"])
def atualizar_endereco(id_endereco: int):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        campos = ["logradouro", "numero", "bairro", "cidade", "estado", "cep"]
        ok, erro = _campos_obrigatorios(data, campos)
        if not ok:
            return jsonify({"erro": erro}), 400

        if len(str(data["estado"])) != 2:
            return jsonify({"erro": "estado deve ter exatamente 2 caracteres (ex: SP)."}), 400

        endereco = update_endereco(
            id_endereco = id_endereco,
            logradouro  = str(data["logradouro"])[:255],
            numero      = str(data["numero"])[:10],
            bairro      = str(data["bairro"])[:100],
            cidade      = str(data["cidade"])[:100],
            estado      = str(data["estado"]).upper()[:2],
            cep         = str(data["cep"])[:9],
        )

        if not endereco:
            return jsonify({"erro": "Endereço não encontrado."}), 404

        return jsonify(endereco), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar endereço.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# DELETE /enderecos/<id>
# ---------------------------------------------------------------------------
@endereco_bp.route("/<int:id_endereco>", methods=["DELETE"])
def deletar_endereco(id_endereco: int):
    try:
        deletado = delete_endereco(id_endereco)

        if not deletado:
            return jsonify({"erro": "Endereço não encontrado."}), 404

        return jsonify({"mensagem": "Endereço deletado com sucesso."}), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao deletar endereço.", "detalhe": str(e)}), 500