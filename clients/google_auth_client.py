import gspread
from typing import Final
from google.oauth2.service_account import Credentials

SCOPES: Final = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def create_gspread_client(credentials_path: str) -> gspread.Client:
    """
    MVP0-safe Google Sheets authentication factory.

    Rules:
    - No environment loading
    - No globals
    - No caching
    - No retries
    - No refresh logic
    """

    if not credentials_path:
        raise ValueError("Google Sheets credentials path is required")

    creds = Credentials.from_service_account_file(
        credentials_path,
        scopes=SCOPES,
    )

    return gspread.authorize(creds)