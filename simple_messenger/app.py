''' app.py '''
import os

from flask import Flask, jsonify
from flask_migrate import Migrate

from simple_messenger.models import db


def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    Migrate(app, db)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'status': 'NOT_FOUND'}), 404

    @app.route('/health')
    def health():
        return jsonify({'status': 'OK'}), 200

    return app
