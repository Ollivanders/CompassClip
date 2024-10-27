from flask import Flask


def create_app():
    app = Flask(__name__)

    return app

    @app.route("/")
    def index():
        return "Hello, world"
