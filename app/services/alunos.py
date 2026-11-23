from datetime import datetime
from zoneinfo import ZoneInfo
from app.repositories import alunos
from app.services.auth import normalizar_telefone
from app.services.erros import ErroNegocio


def _hoje():
    # usa o horário de Fortaleza, e não o do servidor (que pode ser UTC)
    return datetime.now(ZoneInfo("America/Fortaleza")).date().isoformat()


def _validar(nome, telefone, senha):
    nome = (nome or "").strip()
    telefone = normalizar_telefone(telefone or "")
    senha = str(senha or "").strip()

    if not nome:
        raise ErroNegocio("Informe o nome completo")
    if len(telefone) not in (10, 11):
        raise ErroNegocio("Telefone inválido. Informe o DDD e o número")
    if not senha.isdigit() or len(senha) < 4:
        raise ErroNegocio("A senha deve ter somente números, no mínimo 4")
    return nome, telefone, senha


def _telefone_em_uso(telefone, ignorar_id=None):
    existente = alunos.buscar(telefone=telefone)
    return existente is not None and existente["id"] != ignorar_id


def cadastrar(nome, telefone, senha):
    nome, telefone, senha = _validar(nome, telefone, senha)
    if _telefone_em_uso(telefone):
        raise ErroNegocio("Já existe um aluno com esse telefone", 409)
    return alunos.inserir({
        "nome": nome,
        "telefone": telefone,
        "senha": senha,
        "data_cadastro": _hoje(),
    })


def listar(busca="", mes="", ano=""):
    resultado = alunos.listar()
    busca = busca.strip().lower()
    if busca:
        digitos = normalizar_telefone(busca)
        resultado = [
            a for a in resultado
            if busca in a["nome"].lower() or (digitos and digitos in a["telefone"])
        ]
    if ano:
        resultado = [a for a in resultado if a["data_cadastro"][:4] == str(ano)]
    if mes:
        resultado = [a for a in resultado if a["data_cadastro"][5:7] == str(mes).zfill(2)]
    return sorted(resultado, key=lambda a: a["nome"].lower())


def obter(aluno_id):
    aluno = alunos.buscar(id=aluno_id)
    if not aluno:
        raise ErroNegocio("Aluno não encontrado", 404)
    return aluno


def editar(aluno_id, nome, telefone, senha):
    obter(aluno_id)
    nome, telefone, senha = _validar(nome, telefone, senha)
    if _telefone_em_uso(telefone, ignorar_id=aluno_id):
        raise ErroNegocio("Já existe um aluno com esse telefone", 409)
    # data_cadastro não entra aqui, então é preservada
    return alunos.atualizar(
        {"id": aluno_id},
        {"nome": nome, "telefone": telefone, "senha": senha},
    )


def remover(aluno_id):
    obter(aluno_id)
    alunos.apagar(id=aluno_id)


def remover_lote(ids):
    if not ids:
        raise ErroNegocio("Selecione ao menos um aluno")
    return sum(alunos.apagar(id=i) for i in ids)