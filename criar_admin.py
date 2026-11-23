import getpass
from werkzeug.security import generate_password_hash
from app.repositories import config

senha = getpass.getpass("Nova senha administrativa: ")
hash_senha = generate_password_hash(senha)

if config.buscar(chave="senha_admin"):
    config.atualizar({"chave": "senha_admin"}, {"valor": hash_senha})
else:
    config.inserir({"chave": "senha_admin", "valor": hash_senha})

print("Senha administrativa definida.")