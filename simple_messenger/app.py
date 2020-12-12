''' app.py '''
from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'status': 'NOT_FOUND'}), 404

    @app.route('/health')
    def health():
        return jsonify({'status': 'OK'}), 200

    return app
