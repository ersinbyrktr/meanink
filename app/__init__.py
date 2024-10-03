# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import config
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    # Register blueprints
    from app.routes.notes import notes_bp
    from app.routes.search import search_bp
    from app.routes.categories import categories_bp

    app.register_blueprint(notes_bp, url_prefix='/notes')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(categories_bp, url_prefix='/categories')

    return app
