import re
from datetime import datetime
from app.repositories import eventos, tipos_evento
from app.services.erros import ErroNegocio

COR_PADRAO = "#6b7280"


# ---------- validações ----------
def _validar_data(valor):
    try:
        return datetime.strptime(str(valor), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ErroNegocio("Data inválida. Use o formato AAAA-MM-DD")


def _validar_hora(valor, campo):
    if not valor:
        return ""
    try:
        return datetime.strptime(str(valor), "%H:%M").strftime("%H:%M")
    except ValueError:
        raise ErroNegocio(f"{campo} inválido. Use o formato HH:MM")


def _validar_tipo(tipo):
    tipo = (tipo or "").strip().lower()
    for t in tipos_evento.listar():
        if t["nome"].lower() == tipo:
            return t["nome"]          # devolve com a grafia cadastrada
    raise ErroNegocio("Tipo de evento inexistente")


def _validar(c):
    inicio = _validar_hora(c.get("hora_inicio"), "Horário de início")
    fim = _validar_hora(c.get("hora_fim"), "Horário de término")
    if inicio and fim and fim <= inicio:
        raise ErroNegocio("O horário de término deve ser depois do início")
    return {
        "data": _validar_data(c.get("data")),
        "hora_inicio": inicio,
        "hora_fim": fim,
        "tipo": _validar_tipo(c.get("tipo")),
        "disciplina": (c.get("disciplina") or "").strip(),
        "catequista": (c.get("catequista") or "").strip(),
        "observacoes": (c.get("observacoes") or "").strip(),
    }


def _com_cor(lista):
    """Anexa a cor do tipo, para o front pintar o calendário."""
    cores = {t["nome"]: t["cor"] for t in tipos_evento.listar()}
    for e in lista:
        e["cor"] = cores.get(e["tipo"], COR_PADRAO)
    return lista


# ---------- eventos ----------
def listar(mes="", ano=""):
    resultado = eventos.listar()
    if ano:
        resultado = [e for e in resultado if e["data"][:4] == str(ano)]
    if mes:
        resultado = [e for e in resultado if e["data"][5:7] == str(mes).zfill(2)]
    resultado.sort(key=lambda e: (e["data"], e["hora_inicio"]))
    return _com_cor(resultado)


def obter(evento_id):
    evento = eventos.buscar(id=evento_id)
    if not evento:
        raise ErroNegocio("Evento não encontrado", 404)
    return _com_cor([evento])[0]


def criar(corpo):
    return _com_cor([eventos.inserir(_validar(corpo))])[0]


def editar(evento_id, corpo):
    obter(evento_id)
    atualizado = eventos.atualizar({"id": evento_id}, _validar(corpo))
    return _com_cor([atualizado])[0]


def remover(evento_id):
    obter(evento_id)
    eventos.apagar(id=evento_id)


# ---------- tipos de evento ----------
def listar_tipos():
    return tipos_evento.listar()


def criar_tipo(nome, cor):
    nome = (nome or "").strip()
    cor = (cor or COR_PADRAO).strip()
    if not nome:
        raise ErroNegocio("Informe o nome do tipo")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", cor):
        raise ErroNegocio("Cor inválida. Use o formato #RRGGBB")
    if any(t["nome"].lower() == nome.lower() for t in tipos_evento.listar()):
        raise ErroNegocio("Esse tipo já existe", 409)
    return tipos_evento.inserir({"nome": nome, "cor": cor})