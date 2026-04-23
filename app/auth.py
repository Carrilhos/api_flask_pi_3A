import jwt
from functools import wraps
from flask import request, jsonify, current_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verifica se o token veio no cabeçalho Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # O padrão é "Bearer <token>", então pegamos a segunda parte
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"erro": "Formato do token inválido. Use 'Bearer <token>'"}), 401

        if not token:
            return jsonify({"erro": "Token de autenticação ausente."}), 401

        try:
            # Decodifica o token usando a SECRET_KEY do seu app
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # Extrai o id_usuario que salvamos no payload durante o login
            current_user_id = data['id_usuario']
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "O token expirou. Faça login novamente."}), 401
        except Exception as e:
            return jsonify({"erro": "Token inválido.", "detalhe": str(e)}), 401

        # Retorna a função original passando o id_usuario como primeiro argumento
        return f(current_user_id, *args, **kwargs)

    return decorated