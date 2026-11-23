from flask import Blueprint, request, jsonify
from app.services import eventos as servico
from app.services.auth import exigir_login

bp = Blueprint("eventos", __name__, url_prefix="/eventos")
bp_tipos = Blueprint("tipos_evento", __name__, url_prefix="/tipos-evento")


def _corpo():
    return request.get_json(silent=True) or {}


# ----- leitura: admin e aluno -----
@bp.get("")
@exigir_login("admin", "aluno")
def listar():
    return jsonify(servico.listar(
        mes=request.args.get("mes", ""),
        ano=request.args.get("ano", ""),
    ))


@bp.get("/<evento_id>")
@exigir_login("admin", "aluno")
def obter(evento_id):
    return jsonify(servico.obter(evento_id))


@bp_tipos.get("")
@exigir_login("admin", "aluno")
def listar_tipos():
    return jsonify(servico.listar_tipos())


# ----- escrita: só admin -----
@bp.post("")
@exigir_login("admin")
def criar():
    return jsonify(servico.criar(_corpo())), 201


@bp.put("/<evento_id>")
@exigir_login("admin")
def editar(evento_id):
    return jsonify(servico.editar(evento_id, _corpo()))


@bp.delete("/<evento_id>")
@exigir_login("admin")
def remover(evento_id):
    servico.remover(evento_id)
    return jsonify(mensagem="Evento removido")


@bp_tipos.post("")
@exigir_login("admin")
def criar_tipo():
    c = _corpo()
    return jsonify(servico.criar_tipo(c.get("nome"), c.get("cor"))), 201