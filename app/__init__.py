from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=app.config["CORS_ORIGINS"])
    
    from .services.erros import ErroNegocio

    @app.errorhandler(ErroNegocio)
    def tratar_erro(e):
        return jsonify(erro=e.mensagem), e.status

    from gspread.exceptions import APIError

    @app.errorhandler(APIError)
    def erro_google(e):
        return jsonify(
            erro="O serviço de dados está ocupado. Tente novamente em instantes."
        ), 503

    @app.get("/saude")
    def saude():
        return jsonify({"status": "ok"})
    
    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .routes.alunos import bp as alunos_bp
    app.register_blueprint(alunos_bp)

    from .routes.eventos import bp as eventos_bp, bp_tipos
    app.register_blueprint(eventos_bp)
    app.register_blueprint(bp_tipos)

    from .routes.frequencia import bp as frequencia_bp
    app.register_blueprint(frequencia_bp)

    from .routes.configuracoes import bp as configuracoes_bp
    app.register_blueprint(configuracoes_bp)

    return app