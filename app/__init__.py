from flask import Flask
from multi_cloud_allocation.app.routes import bp as routes_blueprint


def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes_blueprint)
    return app
