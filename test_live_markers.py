# test_live_markers.py
from services.google_auth_service import create_gspread_client
from services.sheets_markers_reader import SheetsMarkersReader
from config.static_config import GOOGLE_SHEETS_CONSTANTS

from dotenv import load_dotenv
import os 

def main():
    # 1️⃣ Provide the path to your service account JSON
    load_dotenv()
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    print(f"Credentials Path : {credentials_path}")

    # 2️⃣ Create authenticated gspread client
    client = create_gspread_client(credentials_path)
    print("Client Created sucessfully")

    # 3️⃣ Initialize SheetsMarkersReader
    reader = SheetsMarkersReader(client)

    # 4️⃣ Fetch markers from the live Google Sheet
    try:
        markers = reader.fetch_markers()
        print("✅ Markers fetched successfully:")
        for key, value in markers.items():
            print(f" - {key}: {value}")
    except RuntimeError as e:
        print("❌ Error fetching markers:")
        print(e)


if __name__ == "__main__":
    main()
