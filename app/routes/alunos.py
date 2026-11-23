from flask import Blueprint, request, jsonify
from app.services import alunos as servico
from app.services.auth import exigir_login
from app.services.erros import ErroNegocio

bp = Blueprint("alunos", __name__, url_prefix="/alunos")


@bp.errorhandler(ErroNegocio)
def tratar_erro(e):
    return jsonify(erro=e.mensagem), e.status


def _corpo():
    return request.get_json(silent=True) or {}


@bp.post("")
@exigir_login("admin")
def cadastrar():
    c = _corpo()
    aluno = servico.cadastrar(c.get("nome"), c.get("telefone"), c.get("senha"))
    return jsonify(aluno), 201


@bp.get("")
@exigir_login("admin")
def listar():
    return jsonify(servico.listar(
        busca=request.args.get("busca", ""),
        mes=request.args.get("mes", ""),
        ano=request.args.get("ano", ""),
    ))


@bp.get("/<aluno_id>")
@exigir_login("admin")
def obter(aluno_id):
    return jsonify(servico.obter(aluno_id))


@bp.put("/<aluno_id>")
@exigir_login("admin")
def editar(aluno_id):
    c = _corpo()
    aluno = servico.editar(aluno_id, c.get("nome"), c.get("telefone"), c.get("senha"))
    return jsonify(aluno)


@bp.delete("/<aluno_id>")
@exigir_login("admin")
def remover(aluno_id):
    servico.remover(aluno_id)
    return jsonify(mensagem="Aluno removido")


@bp.post("/remover-lote")
@exigir_login("admin")
def remover_lote():
    total = servico.remover_lote(_corpo().get("ids", []))
    return jsonify(removidos=total)