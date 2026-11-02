# app/__init__.py
# Flask application factory.
# Registers the blueprint from routes.py.

from flask import Flask
from config import Config
from models import db


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(config_class)

    db.init_app(app)

    from app.routes import bp
    app.register_blueprint(bp)

    return app