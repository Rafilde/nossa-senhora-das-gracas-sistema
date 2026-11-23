import gspread
from google.oauth2.service_account import Credentials
from app.config import Config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

ABAS = {
    "alunos": ["id", "nome", "telefone", "senha", "data_cadastro"],
    "eventos": ["id", "data", "hora_inicio", "hora_fim", "tipo",
                "disciplina", "catequista", "observacoes"],
    "tipos_evento": ["nome", "cor"],
    "frequencia": ["aluno_id", "aluno_nome", "data", "situacao"],
    "config": ["chave", "valor"],
}

TIPOS_INICIAIS = [
    ["Aula", "#2563eb"],
    ["Feriado", "#dc2626"],
    ["Retiro", "#16a34a"],
    ["Recesso", "#f59e0b"],
]

creds = Credentials.from_service_account_file(
    Config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
)
planilha = gspread.authorize(creds).open_by_key(Config.SPREADSHEET_ID)

existentes = [ws.title for ws in planilha.worksheets()]

for nome, colunas in ABAS.items():
    if nome in existentes:
        print(f"'{nome}' já existe, pulando.")
        continue
    ws = planilha.add_worksheet(title=nome, rows=1000, cols=len(colunas))
    ws.format("A:Z", {"numberFormat": {"type": "TEXT"}})  # tudo como texto
    ws.append_row(colunas)
    ws.freeze(rows=1)
    ws.format("1:1", {"textFormat": {"bold": True}})
    print(f"'{nome}' criada.")

# tipos iniciais de evento
ws_tipos = planilha.worksheet("tipos_evento")
if len(ws_tipos.get_all_values()) <= 1:
    ws_tipos.append_rows(TIPOS_INICIAIS)
    print("Tipos de evento iniciais adicionados.")

# remove a aba padrão vazia, se existir
for padrao in ("Sheet1", "Página1", "Planilha1"):
    if padrao in existentes and len(planilha.worksheets()) > 1:
        planilha.del_worksheet(planilha.worksheet(padrao))

print("Pronto!")