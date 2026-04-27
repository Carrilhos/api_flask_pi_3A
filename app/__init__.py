from flask import Flask
from flask_cors import CORS
from app.config import Config

#Pai nosso que estais nos Céus,
#santificado seja o vosso Nome,
#venha a nós o vosso Reino,
#seja feita a vossa vontade assim na terra como no Céu.
#O pão nosso de cada dia nos dai hoje,
#perdoai-nos as nossas ofensas
#assim como nós perdoamos a quem nos tem ofendido,
#e não nos deixeis cair em tentação,
#mas livrai-nos do Mal.
#Amém.

#Garantia que vai funcionar
print("INIT EXECUTADO")

def register_routes(app):
    """Registra todos os Blueprints (rotas) da aplicação no app Flask."""
    from app.routes.product_routes import produto_bp
    from app.routes.category_routes import category_bp
    from app.routes.pedido_routes import pedido_bp
    from app.routes.anuncio_routes import anuncio_bp
    from app.routes.usuario_routes import usuario_bp # Importa aqui dentro
    from app.routes.endereco_routes import endereco_bp
    
    app.register_blueprint(produto_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(anuncio_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(endereco_bp)

def create_app():
    """Factory function para criar, configurar e retornar a instância da aplicação Flask com CORS e Blueprints."""
    app = Flask(__name__)
    # Diz para o Flask parar de ordenar as chaves do JSON em ordem alfabética
    app.json.sort_keys = False
    app.config.from_object(Config)
    
    app.config['SECRET_KEY'] = 'projeto_pi_3a_secret_key'
    # ---------------------------------

    CORS(app, origins=[
        "http://localhost:3000",
        "https://front-pi-3-a.vercel.app",
    ])

    register_routes(app)

    print(app.url_map)

    return app