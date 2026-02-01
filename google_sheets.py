import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_NAME, SHEET_INDEX

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file(
    "google_key.json",
    scopes=SCOPES
)

gc = gspread.authorize(CREDS)

def get_ws():
    sh = gc.open(SPREADSHEET_NAME)
    return sh.get_worksheet(SHEET_INDEX)

def find_user_row(username):
    ws = get_ws()
    col = ws.col_values(1)
    for i, val in enumerate(col, start=1):
        if val == username:
            return i
    return None

def upsert_participant(username, nickname, total_bm, squad_bm):
    ws = get_ws()
    row = find_user_row(username)

    values = [username, nickname, total_bm, squad_bm]

    if row:
        ws.update(f"A{row}:D{row}", [values])
    else:
        ws.append_row(values, value_input_option="USER_ENTERED")

def delete_participant(username):
    ws = get_ws()
    row = find_user_row(username)
    if row:
        ws.delete_rows(row)

def get_all_participants():
    ws = get_ws()
    return ws.get_all_values()[1:]  # без заголовков
