import hmac
from functools import wraps
from flask import request, jsonify, g, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature
from werkzeug.security import check_password_hash
from app.repositories import alunos, config

VALIDADE_SEGUNDOS = 60 * 60 * 12   # token vale 12 horas


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def gerar_token(dados):
    return _serializer().dumps(dados)


def validar_token(token):
    try:
        return _serializer().loads(token, max_age=VALIDADE_SEGUNDOS)
    except BadSignature:        # assinatura falsa ou token expirado
        return None


def normalizar_telefone(telefone):
    """'(85) 99999-0000' vira '85999990000'."""
    return "".join(c for c in str(telefone) if c.isdigit())


def login_admin(senha):
    registro = config.buscar(chave="senha_admin")
    if not registro or not check_password_hash(registro["valor"], senha):
        return None
    return gerar_token({"papel": "admin"})


def login_aluno(telefone, senha):
    aluno = alunos.buscar(telefone=normalizar_telefone(telefone))
    if not aluno or not hmac.compare_digest(aluno["senha"], str(senha)):
        return None
    token = gerar_token({"papel": "aluno", "id": aluno["id"]})
    return token, aluno


def exigir_login(*papeis):
    """Decorador: só deixa passar quem tem token válido e o papel certo."""
    def decorador(funcao):
        @wraps(funcao)
        def wrapper(*args, **kwargs):
            cabecalho = request.headers.get("Authorization", "")
            dados = None
            if cabecalho.startswith("Bearer "):
                dados = validar_token(cabecalho[7:])
            if not dados:
                return jsonify(erro="Não autenticado"), 401
            if dados["papel"] not in papeis:
                return jsonify(erro="Sem permissão"), 403
            g.usuario = dados
            return funcao(*args, **kwargs)
        return wrapper
    return decorador