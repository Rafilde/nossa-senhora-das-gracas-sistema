from werkzeug.security import generate_password_hash
from app.repositories import alunos, eventos, frequencia, config
from app.services.erros import ErroNegocio

PALAVRA_CONFIRMACAO = "DELETAR"
TAMANHO_MINIMO_SENHA = 4


def trocar_senha_admin(nova_senha):
    nova_senha = str(nova_senha or "").strip()
    if len(nova_senha) < TAMANHO_MINIMO_SENHA:
        raise ErroNegocio(
            f"A senha deve ter no mínimo {TAMANHO_MINIMO_SENHA} caracteres"
        )

    hash_senha = generate_password_hash(nova_senha)
    if config.buscar(chave="senha_admin"):
        config.atualizar({"chave": "senha_admin"}, {"valor": hash_senha})
    else:
        config.inserir({"chave": "senha_admin", "valor": hash_senha})


def deletar_tudo(confirmacao):
    if str(confirmacao or "").strip() != PALAVRA_CONFIRMACAO:
        raise ErroNegocio(f"Digite {PALAVRA_CONFIRMACAO} para confirmar")

    removidos = {
        "alunos": len(alunos.listar()),
        "frequencia": len(frequencia.listar()),
        "eventos": len(eventos.listar()),
    }
    frequencia.apagar_tudo()
    alunos.apagar_tudo()
    eventos.apagar_tudo()
    return removidos