from flask import Flask
from app.config import Config
print("INIT EXECUTADO")
def register_routes(app):
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    from app.routes.product_routes import produto_bp
    app.register_blueprint(produto_bp)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_routes(app)

    print(app.url_map)

    return app
