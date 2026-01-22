# test_live_markers.py
from clients.google_auth_client import create_gspread_client
from services.sheets_markers_reader import SheetsMarkersReader
from models.system_logger import ETLLogger

from config.static_config import GOOGLE_SHEETS_CONSTANTS

from dotenv import load_dotenv
import os 

etl_loger = ETLLogger()
logger = etl_loger.get_logger(file=__file__)

def main():
    # 1️⃣ Provide the path to your service account JSON
    load_dotenv()
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    logger.info(f"Google Auth credentials fetched successfully")

    # 2️⃣ Create authenticated gspread client
    logger.info("Attempting to create gspread client")
    client = create_gspread_client(credentials_path)
    logger.info("gspread lient created successfully")
    # 3️⃣ Initialize SheetsMarkersReader
    reader = SheetsMarkersReader(client)

    # 4️⃣ Fetch markers from the live Google Sheet
    try:
        markers = reader.fetch_markers()
        for key, value in markers.items():
            print(f" - {key}: {value}")
    except RuntimeError as e:
        logger.error(" Error fetching markers:")
        logger.error(e)


if __name__ == "__main__":
    main()
