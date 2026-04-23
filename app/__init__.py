from flask import Flask
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
    from app.routes.product_routes import produto_bp
    from app.routes.category_routes import category_bp
    app.register_blueprint(produto_bp)
    app.register_blueprint(category_bp)

def create_app():
    app = Flask(__name__)
    # Diz para o Flask parar de ordenar as chaves do JSON em ordem alfabética
    app.json.sort_keys = False
    app.config.from_object(Config)

    register_routes(app)

    print(app.url_map)

    return app

def register_routes(app):
    from app.routes.product_routes import produto_bp
    from app.routes.pedido_routes import pedido_bp
    from app.routes.anuncio_routes import anuncio_bp

    app.register_blueprint(produto_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(anuncio_bp)

    from app.routes.usuario_routes import usuario_bp
    app.register_blueprint(usuario_bp)