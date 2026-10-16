from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS


from .config import Config
from .models import db
from .auth.routes import auth_bp
from .service_requests.routes import request_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    # Keep the rest of your existing setup unchanged


    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # Register FixFlow modules
    app.register_blueprint(auth_bp)
    app.register_blueprint(request_bp)

    @app.route("/")
    def home():
        return {
            "application": "FixFlow",
            "message": "FixFlow API is running!"
        }

    return app