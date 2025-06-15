from flask import Flask, request, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def add_cache_header(response):
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.before_request
    def enforce_json_only():
        if request.method == 'POST' and not request.is_json:
            return jsonify({"error": "Only JSON supported"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.route("/<path:any>", methods=["PUT", "DELETE", "PATCH"])
    def method_not_allowed(any):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    from .routes.dictionary import dictionary_bp
    from .routes.ocr import ocr_bp
    from .routes.sync import sync_bp
    from .routes.system import system_bp
    app.register_blueprint(dictionary_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(system_bp)

    return app
