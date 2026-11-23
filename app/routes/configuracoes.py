from flask import Blueprint, request, jsonify
from app.services import configuracoes as servico
from app.services.auth import exigir_login

bp = Blueprint("configuracoes", __name__, url_prefix="/configuracoes")


@bp.put("/senha-admin")
@exigir_login("admin")
def trocar_senha():
    c = request.get_json(silent=True) or {}
    servico.trocar_senha_admin(c.get("nova_senha"))
    return jsonify(mensagem="Senha alterada com sucesso")


@bp.post("/deletar-tudo")
@exigir_login("admin")
def deletar_tudo():
    c = request.get_json(silent=True) or {}
    removidos = servico.deletar_tudo(c.get("confirmacao"))
    return jsonify(mensagem="Dados apagados", removidos=removidos)