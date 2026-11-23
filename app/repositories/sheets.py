import gspread
from google.oauth2.service_account import Credentials
from app.config import Config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_planilha = None

def get_planilha():
    """Abre a planilha uma única vez e reaproveita a conexão."""
    global _planilha
    if _planilha is None:
        creds = Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        _planilha = gspread.authorize(creds).open_by_key(Config.SPREADSHEET_ID)
    return _planilha