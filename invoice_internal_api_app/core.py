from flask import Flask
from flask_restful import Api

from .urls import setup_blueprints


def create_app():
    """Create web app."""
    app = Flask(__name__)
    api = Api(app)
    setup_blueprints(api)
    return app
