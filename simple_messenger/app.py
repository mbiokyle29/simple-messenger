''' app.py '''
import os

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from yaml import safe_load

from simple_messenger.exceptions import SimpleMessengerException
from simple_messenger.models import db
from simple_messenger.views import api


def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(api)

    db.init_app(app)
    Migrate(app, db)

    swagger_path = os.path.join(
        os.path.dirname(__file__),
        'static/swagger.yml',
    )
    swagger_yml = safe_load(open(swagger_path, 'r'))
    blueprint = get_swaggerui_blueprint(
        '/docs',
        swagger_path,
        config={'spec': swagger_yml},
    )
    app.register_blueprint(blueprint)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'NOT_FOUND',
            'message': f'No resource found at: {request.path}',
        }), 404

    @app.errorhandler(SimpleMessengerException)
    def application_exception(error):
        return jsonify({
            'status': error.status,
            'message': error.message,
        }), error.status_code

    @app.route('/health')
    def health():
        return jsonify({'status': 'OK'}), 200

    return app
