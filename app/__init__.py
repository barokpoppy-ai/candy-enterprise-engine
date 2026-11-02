# app/__init__.py
# Flask application factory.

from flask import Flask
from config import Config
from models import db


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(config_class)

    db.init_app(app)

    # Routes are registered in a later batch.
    return app