from app.auth import token_required
from flask import Blueprint, request, jsonify
from app.repositories.endereco_repository import (
    create_endereco,
    update_endereco,
    delete_endereco
)

# ---------------------------------------------------------------------------
# Blueprint - Padronizado para /enderecos
# ---------------------------------------------------------------------------
endereco_bp = Blueprint("endereco", __name__, url_prefix="/enderecos")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _campos_obrigatorios(data: dict, campos: list):
    faltando = [c for c in campos if c not in data or data[c] is None]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None

# ---------------------------------------------------------------------------
# POST /enderecos → cria um novo endereço (PROTEGIDA)
# ---------------------------------------------------------------------------
@endereco_bp.route("/", methods=["POST"])
@token_required 
def criar_endereco(current_user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        campos_necessarios = ["logradouro", "numero", "bairro", "cidade", "estado", "cep"]
        ok, erro = _campos_obrigatorios(data, campos_necessarios)
        if not ok:
            return jsonify({"erro": erro}), 400

        endereco = create_endereco(
            id_usuario=current_user_id, 
            logradouro=data["logradouro"],
            numero=data["numero"],
            bairro=data["bairro"],
            cidade=data["cidade"],
            estado=data["estado"],
            cep=data["cep"]
        )
        return jsonify(endereco), 201
    except Exception as e:
        return jsonify({"erro": "Erro ao criar endereço.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# PUT /enderecos/<id> → atualiza um endereço completo
# ---------------------------------------------------------------------------
@endereco_bp.route("/<int:id_endereco>", methods=["PUT"])
def atualizar_endereco(id_endereco: int):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        campos_necessarios = ["logradouro", "numero", "bairro", "cidade", "estado", "cep"]
        ok, erro = _campos_obrigatorios(data, campos_necessarios)
        if not ok:
            return jsonify({"erro": erro}), 400

        endereco = update_endereco(
            id_endereco=id_endereco,
            logradouro=data["logradouro"],
            numero=data["numero"],
            bairro=data["bairro"],
            cidade=data["cidade"],
            estado=data["estado"],
            cep=data["cep"]
        )

        if not endereco:
            return jsonify({"erro": "Endereço não encontrado."}), 404
        return jsonify(endereco), 200
    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar endereço.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# DELETE /enderecos/<id> → remove um endereço
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