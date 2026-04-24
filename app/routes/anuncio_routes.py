from app.repositories.usuario_repository import find_usuario_by_id
from app.auth import token_required
from flask import Blueprint, request, jsonify
from app.repositories.anuncio_repository import (
    find_all_anuncios,
    find_anuncios_by_vendedor,
    find_anuncio_by_id,
)
from app.services.anuncio_service import (
    criar_anuncio_service,
    obter_anuncio_completo,
    atualizar_anuncio_service,
    atualizar_estoque_service,
    deletar_anuncio_service,
)

# ---------------------------------------------------------------------------
# Blueprint - Padronizado para /anuncios
# ---------------------------------------------------------------------------
anuncio_bp = Blueprint("anuncio", __name__, url_prefix="/anuncios")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _campos_obrigatorios(data: dict, campos: list):
    faltando = [c for c in campos if c not in data or data[c] is None]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None


# ---------------------------------------------------------------------------
# GET /anuncios  →  lista todos (filtro opcional por id_vendedor)
# ---------------------------------------------------------------------------
@anuncio_bp.route("/", methods=["GET"])
def listar_anuncios():
    try:
        id_vendedor = request.args.get("id_vendedor", type=int)

        if id_vendedor:
            anuncios = find_anuncios_by_vendedor(id_vendedor)
        else:
            anuncios = find_all_anuncios()

        return jsonify(anuncios), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao listar anúncios.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# GET /anuncios/<id>  →  busca um anúncio pelo ID
# ---------------------------------------------------------------------------
@anuncio_bp.route("/<int:id_anuncio>", methods=["GET"])
def buscar_anuncio(id_anuncio: int):
    try:
        anuncio = find_anuncio_by_id(id_anuncio)

        if not anuncio:
            return jsonify({"erro": "Anúncio não encontrado."}), 404

        return jsonify(anuncio), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao buscar anúncio.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# GET /anuncios/<id>/detalhes  →  busca detalhes completos
# ---------------------------------------------------------------------------
@anuncio_bp.route("/<int:id_anuncio>/detalhes", methods=["GET"])
def detalhe_anuncio(id_anuncio):
    try:
        detalhe = obter_anuncio_completo(id_anuncio)
        
        if not detalhe:
            return jsonify({"erro": "Anúncio não encontrado."}), 404
            
        return jsonify(detalhe), 200

    except Exception as e:
        return jsonify({"erro": "Erro ao buscar detalhes do anúncio.", "detalhe": str(e)}), 500

# ---------------------------------------------------------------------------
# POST /anuncios  →  cria um novo anúncio (PROTEGIDA)
# ---------------------------------------------------------------------------
@anuncio_bp.route("/", methods=["POST"])
@token_required
def criar_anuncio(current_user_id):
    try:
        # --- VALIDAÇÃO DE PERMISSÃO (VENDEDOR) ---
        usuario_logado = find_usuario_by_id(current_user_id)

        if not usuario_logado or usuario_logado.get("tipo_usuario") != "VENDEDOR":
            return jsonify({
                "erro": "Acesso negado.",
                "detalhe": "Apenas usuários com perfil VENDEDOR podem criar anúncios."
            }), 403 
        # ------------------------------------------

        data = request.form
        imagens = request.files.getlist("imagens")
        imagem_principal = request.form.get("imagem_principal", 0)

        if not data:
            return jsonify({"erro": "Form data inválido."}), 400

        anuncio = criar_anuncio_service(
            data=data,
            imagens=imagens,
            imagem_principal=imagem_principal,
            id_usuario=current_user_id 
        )

        return jsonify(anuncio), 201

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({
            "erro": "Erro ao criar anúncio.",
            "detalhe": str(e)
        }), 500
    
    
# ---------------------------------------------------------------------------
# PUT /anuncios/<id>  →  atualiza um anúncio completo
# ---------------------------------------------------------------------------
@anuncio_bp.route("/<int:id_anuncio>", methods=["PUT"])
@token_required
def atualizar_anuncio(current_user_id, id_anuncio: int):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

        anuncio = atualizar_anuncio_service(id_anuncio, current_user_id, data)
        return jsonify(anuncio), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400 if "não encontrado" not in str(e) else 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar anúncio.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# PATCH /anuncios/<id>/estoque  →  atualiza apenas o estoque
# ---------------------------------------------------------------------------
@anuncio_bp.route("/<int:id_anuncio>/estoque", methods=["PATCH"])
@token_required
def atualizar_estoque(current_user_id, id_anuncio: int):
    try:
        data = request.get_json()
        if not data or "estoque" not in data:
            return jsonify({"erro": "Campo 'estoque' é obrigatório."}), 400

        anuncio = atualizar_estoque_service(id_anuncio, current_user_id, data["estoque"])
        return jsonify(anuncio), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400 if "não encontrado" not in str(e) else 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar estoque.", "detalhe": str(e)}), 500


# ---------------------------------------------------------------------------
# DELETE /anuncios/<id>  →  remove um anúncio
# ---------------------------------------------------------------------------
@anuncio_bp.route("/<int:id_anuncio>", methods=["DELETE"])
@token_required
def deletar_anuncio_rota(current_user_id, id_anuncio: int):
    try:
        deletar_anuncio_service(id_anuncio, current_user_id)
        return jsonify({"mensagem": "Anúncio deletado com sucesso."}), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except Exception as e:
        return jsonify({"erro": "Erro ao deletar anúncio.", "detalhe": str(e)}), 500