# run_batch_context.py
from clients.google_auth_client import create_gspread_client
from services.sheets_markers_reader import SheetsMarkersReader
from services.sheets_order_counters_reader import OrderCountersReader
from services.build_batch_context import build_batch_context
from config.static_config import GOOGLE_SHEETS_CONSTANTS, NOTION_CONSTANTS, WHATSAPP_CONSTANTS
from models.system_logger import ETLLogger

from dotenv import load_dotenv
import os

etl_logger = ETLLogger()
logger = etl_logger.get_logger(file=__file__)

def main():
    # 1️⃣ Load environment variables
    load_dotenv()
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    if not credentials_path:
        logger.critical("GOOGLE_SHEETS_CREDENTIALS_PATH not found in environment")
        return

    # 2️⃣ Create authenticated gspread client
    try:
        logger.info("Creating gspread client")
        client = create_gspread_client(credentials_path)
        logger.info("gspread client created successfully")
    except Exception as e:
        logger.critical("Failed to create gspread client")
        logger.exception(e)
        return

    # 3️⃣ Initialize sheets readers
    markers_reader = SheetsMarkersReader(client)
    order_counters_reader = OrderCountersReader(client)

    # 4️⃣ Build batch context
    try:
        batch_context = build_batch_context(
            sheets_markers_reader=markers_reader,
            sheets_order_counter_reader=order_counters_reader,
            google_sheets_constants=GOOGLE_SHEETS_CONSTANTS,
            notion_constants=NOTION_CONSTANTS,
            whatsapp_constants=WHATSAPP_CONSTANTS,
        )
    except Exception as e:
        logger.critical("Failed to build batch context")
        logger.exception(e)
        return

    # 5️⃣ Print the batch context raw (without formatting))
    print(f"\n --batch_context--\n\n {batch_context}\n\n")

if __name__ == "__main__":
    main()
