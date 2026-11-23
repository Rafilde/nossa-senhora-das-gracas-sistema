from flask import Blueprint, request, jsonify, g
from app.services import frequencia as servico
from app.services.auth import exigir_login

bp = Blueprint("frequencia", __name__, url_prefix="/frequencia")


# ----- admin -----
@bp.post("")
@exigir_login("admin")
def registrar():
    c = request.get_json(silent=True) or {}
    return jsonify(servico.registrar_chamada(c.get("data"), c.get("registros", [])))


@bp.get("/chamada")
@exigir_login("admin")
def chamada():
    return jsonify(servico.chamada(request.args.get("data", "")))


@bp.get("/chamadas")
@exigir_login("admin")
def chamadas():
    return jsonify(servico.listar_chamadas())


@bp.get("/aluno/<aluno_id>")
@exigir_login("admin")
def historico_do_aluno(aluno_id):
    return jsonify(servico.historico_aluno(aluno_id))


# ----- aluno: só os próprios dados -----
@bp.get("/minha")
@exigir_login("aluno")
def minha():
    return jsonify(servico.historico_aluno(g.usuario["id"], so_se_existir=True))