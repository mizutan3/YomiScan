from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    from .routes.dictionary import dictionary_bp
    from .routes.ocr import ocr_bp
    from .routes.sync import sync_bp
    from .routes.system import system_bp

    app.register_blueprint(dictionary_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(system_bp)

    return app
