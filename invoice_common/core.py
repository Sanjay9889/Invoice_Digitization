from flask import Flask


def create_app():
    """Create web app."""
    app = Flask(__name__)
    return app
