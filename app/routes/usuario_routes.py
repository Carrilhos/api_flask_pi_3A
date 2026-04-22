from flask import Blueprint, request, jsonify
from app.repositories.usuario_repository import (
    find_all_usuarios,
    find_usuarios_by_tipo,
    find_usuario_by_id,
    find_usuario_by_email,
    create_usuario,
    update_usuario,
    delete_usuario,
)

# ---------------------------------------------------------------------------
# Blueprint
# ---------------------------------------------------------------------------
usuario_bp = Blueprint("usuario", __name__, url_prefix="/usuarios")

# ---------------------------------------------------------------------------
# Tipos permitidos
# ---------------------------------------------------------------------------
TIPOS_VALIDOS = {"CLIENTE", "VENDEDOR"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _campos_obrigatorios(data: dict, campos: list):
    faltando = [c for c in campos if c not in data or data[c] is None]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None


def _validar_tipo(tipo: str):
    if tipo.upper() not in TIPOS_VALIDOS:
        return False, f"tipo_usuario inválido. Permitidos: {', '.join(TIPOS_VALIDOS)}"
    return True, None


# ---------------------------------------------------------------------------
# GET /usuarios  →  lista todos (filtro opcional por tipo_usuario)
# ---------------------------------------------------------------------------
@usuario_bp.route("/", methods=["GET"])
def listar_usuarios():
    """
    Query params opcionais:
      - tipo_usuario (CLIENTE ou VENDEDOR)
    """
    try:
        tipo = request.args.get("tipo_usuario")

        if tipo:
            ok, erro = _validar_tipo(tipo)
            if not ok:
                return jsonify({"erro": erro}), 400
            usuarios = find_usuarios_by_tipo(tipo.upper())
        else:
            usuarios = find_all_usuarios()

        return jsonify(usuarios), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao listar usuários.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# GET /usuarios/<id>  →  busca um usuário pelo ID
# ---------------------------------------------------------------------------
@usuario_bp.route("/<int:id_usuario>", methods=["GET"])
def buscar_usuario(id_usuario: int):
    try:
        usuario = find_usuario_by_id(id_usuario)

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado."}), 404

        return jsonify(usuario), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao buscar usuário.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# GET /usuarios/email/<email>  →  busca um usuário pelo email
# ---------------------------------------------------------------------------
@usuario_bp.route("/email/<string:email>", methods=["GET"])
def buscar_usuario_por_email(email: str):
    try:
        usuario = find_usuario_by_email(email)

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado."}), 404

        return jsonify(usuario), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao buscar usuário.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# POST /usuarios  →  cria um novo usuário
# ---------------------------------------------------------------------------
@usuario_bp.route("/", methods=["POST"])
def criar_usuario():
    """
    Body JSON esperado:
    {
        "nome":         "Gabriel",
        "sobrenome":    "Carrilhos",
        "email":        "gabriel@email.com",
        "tipo_usuario": "CLIENTE"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        ok, erro = _campos_obrigatorios(data, ["nome", "sobrenome", "email", "tipo_usuario"])
        if not ok:
            return jsonify({"erro": erro}), 400

        ok, erro = _validar_tipo(data["tipo_usuario"])
        if not ok:
            return jsonify({"erro": erro}), 400

        # Verifica se email já existe
        if find_usuario_by_email(data["email"]):
            return jsonify({"erro": "Email já cadastrado."}), 409

        usuario = create_usuario(
            nome         = str(data["nome"]),
            sobrenome    = str(data["sobrenome"]),
            email        = str(data["email"]),
            tipo_usuario = data["tipo_usuario"].upper(),
        )

        return jsonify(usuario), 201

    except Exception as e:
        return jsonify({"erro": "Erro ao criar usuário.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# PUT /usuarios/<id>  →  atualiza um usuário completo
# ---------------------------------------------------------------------------
@usuario_bp.route("/<int:id_usuario>", methods=["PUT"])
def atualizar_usuario(id_usuario: int):
    """
    Body JSON esperado:
    {
        "nome":         "Gabriel",
        "sobrenome":    "Carrilhos",
        "email":        "gabriel@email.com",
        "tipo_usuario": "VENDEDOR"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        ok, erro = _campos_obrigatorios(data, ["nome", "sobrenome", "email", "tipo_usuario"])
        if not ok:
            return jsonify({"erro": erro}), 400

        ok, erro = _validar_tipo(data["tipo_usuario"])
        if not ok:
            return jsonify({"erro": erro}), 400

        # Verifica se o email já pertence a outro usuário
        existente = find_usuario_by_email(data["email"])
        if existente and existente["id_usuario"] != id_usuario:
            return jsonify({"erro": "Email já cadastrado por outro usuário."}), 409

        usuario = update_usuario(
            id_usuario   = id_usuario,
            nome         = str(data["nome"]),
            sobrenome    = str(data["sobrenome"]),
            email        = str(data["email"]),
            tipo_usuario = data["tipo_usuario"].upper(),
        )

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado."}), 404

        return jsonify(usuario), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar usuário.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# DELETE /usuarios/<id>  →  remove um usuário
# ---------------------------------------------------------------------------
@usuario_bp.route("/<int:id_usuario>", methods=["DELETE"])
def deletar_usuario(id_usuario: int):
    try:
        deletado = delete_usuario(id_usuario)

        if not deletado:
            return jsonify({"erro": "Usuário não encontrado."}), 404

        return jsonify({"mensagem": "Usuário deletado com sucesso."}), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao deletar usuário.", "detalhe": str(e)}), 500