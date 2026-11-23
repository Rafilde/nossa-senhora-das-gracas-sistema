from flask import Blueprint, request, jsonify, g
from app.services.auth import login_admin, login_aluno, exigir_login

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/login-admin")
def rota_login_admin():
    corpo = request.get_json(silent=True) or {}
    token = login_admin(corpo.get("senha", ""))
    if not token:
        return jsonify(erro="Senha incorreta"), 401
    return jsonify(token=token, papel="admin")


@bp.post("/login-aluno")
def rota_login_aluno():
    corpo = request.get_json(silent=True) or {}
    resultado = login_aluno(corpo.get("telefone", ""), corpo.get("senha", ""))
    if not resultado:
        return jsonify(erro="Telefone ou senha incorretos"), 401
    token, aluno = resultado
    return jsonify(
        token=token,
        papel="aluno",
        aluno={"id": aluno["id"], "nome": aluno["nome"]},
    )