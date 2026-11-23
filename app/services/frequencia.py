from datetime import datetime
from app.repositories import alunos, frequencia
from app.services.erros import ErroNegocio

SITUACOES = ("presente", "ausente")


def _validar_data(valor):
    try:
        return datetime.strptime(str(valor), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ErroNegocio("Data inválida. Use o formato AAAA-MM-DD")


def registrar_chamada(data, registros):
    """Lança ou corrige a chamada de uma data."""
    data = _validar_data(data)
    if not registros:
        raise ErroNegocio("Informe a situação de ao menos um aluno")

    nomes = {a["id"]: a["nome"] for a in alunos.listar()}
    vistos, linhas = set(), []
    for r in registros:
        aluno_id = str(r.get("aluno_id", ""))
        situacao = str(r.get("situacao", "")).strip().lower()
        if aluno_id not in nomes:
            raise ErroNegocio("Aluno não encontrado", 404)
        if situacao not in SITUACOES:
            raise ErroNegocio("A situação deve ser 'presente' ou 'ausente'")
        if aluno_id in vistos:
            raise ErroNegocio("Aluno repetido na mesma chamada")
        vistos.add(aluno_id)
        linhas.append({
            "aluno_id": aluno_id,
            "aluno_nome": nomes[aluno_id],
            "data": data,
            "situacao": situacao,
        })

    atualizados, novos = frequencia.salvar_lote(["aluno_id", "data"], linhas)
    return {"data": data, "novos": novos, "atualizados": atualizados}


def chamada(data):
    """Lista os alunos com a situação já lançada na data ('' se ainda não houver)."""
    data = _validar_data(data)
    lancados = {r["aluno_id"]: r["situacao"] for r in frequencia.filtrar(data=data)}
    lista = [
        {"aluno_id": a["id"], "nome": a["nome"], "situacao": lancados.get(a["id"], "")}
        for a in alunos.listar()
    ]
    return sorted(lista, key=lambda x: x["nome"].lower())


def listar_chamadas():
    """Chamadas anteriores: uma linha por data, com os totais."""
    por_data = {}
    for r in frequencia.listar():
        d = por_data.setdefault(
            r["data"], {"data": r["data"], "presentes": 0, "ausentes": 0}
        )
        d["presentes" if r["situacao"] == "presente" else "ausentes"] += 1
    return sorted(por_data.values(), key=lambda d: d["data"], reverse=True)


def historico_aluno(aluno_id, so_se_existir=False):
    aluno = alunos.buscar(id=aluno_id)
    registros = frequencia.filtrar(aluno_id=aluno_id)

    if so_se_existir and not aluno:
        raise ErroNegocio("Aluno não encontrado", 404)
    if not aluno and not registros:
        raise ErroNegocio("Aluno não encontrado", 404)

    # aluno removido: o nome vem do próprio histórico
    nome = aluno["nome"] if aluno else registros[0]["aluno_nome"]
    historico = sorted(
        ({"data": r["data"], "situacao": r["situacao"]} for r in registros),
        key=lambda x: x["data"],
        reverse=True,
    )
    return {
        "aluno": {"id": aluno_id, "nome": nome},
        "total_presencas": sum(1 for h in historico if h["situacao"] == "presente"),
        "total_faltas": sum(1 for h in historico if h["situacao"] == "ausente"),
        "historico": historico,
    }