import jwt
import datetime
from flask import current_app
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
# Blueprint - Padronizado para /usuarios
# ---------------------------------------------------------------------------
usuario_bp = Blueprint("usuario", __name__, url_prefix="/usuarios")

# Tipos permitidos no sistema
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

        if find_usuario_by_email(data["email"]):
            return jsonify({"erro": "Email já cadastrado."}), 409

        usuario = create_usuario(
            nome         = str(data["nome"]),
            sobrenome    = str(data["sobrenome"]),
            email        = str(data["email"]),
            tipo_usuario = data["tipo_usuario"].upper(),
            senha        = data.get("senha") # Mantendo a lógica de criação com senha
        )
        return jsonify(usuario), 201
    except Exception as e:
        return jsonify({"erro": "Erro ao criar usuário.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# PUT /usuarios/<id>  →  atualiza um usuário completo
# ---------------------------------------------------------------------------
@usuario_bp.route("/<int:id_usuario>", methods=["PUT"])
def atualizar_usuario(id_usuario: int):
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

# ---------------------------------------------------------------------------
# POST /usuarios/login  →  Faz o login (SHA-256 e JWT)
# ---------------------------------------------------------------------------
@usuario_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        email = data.get('email')
        senha_sha256_recebida = data.get('senha')

        if not email or not senha_sha256_recebida:
            return jsonify({"erro": "Email e senha (SHA-256) são obrigatórios."}), 400

        usuario = find_usuario_by_email(email)

        if usuario and usuario.get('senha') == senha_sha256_recebida:
            payload = {
                "id_usuario": usuario.get('id_usuario'),
                "email": usuario.get('email'),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=3)
            }
            
            token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")
            usuario.pop('senha', None)

            return jsonify({
                "mensagem": "Login realizado com sucesso!",
                "token": token,
                "usuario": usuario
            }), 200
        
        return jsonify({"erro": "Credenciais inválidas."}), 401
    except Exception as e:
        return jsonify({"erro": "Erro interno no servidor.", "detalhe": str(e)}), 500