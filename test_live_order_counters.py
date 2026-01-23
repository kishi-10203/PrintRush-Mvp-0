# test_live_order_counters.py
from clients.google_auth_client import create_gspread_client
from services.sheets_order_counters_reader import OrderCountersReader
from models.system_logger import ETLLogger

from config.static_config import GOOGLE_SHEETS_CONSTANTS

from dotenv import load_dotenv
import os

etl_logger = ETLLogger()
logger = etl_logger.get_logger(file=__file__)

def main():
    # 1️⃣ Load environment variables to get Google service account credentials
    load_dotenv()
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    if not credentials_path:
        logger.critical("GOOGLE_SHEETS_CREDENTIALS_PATH not found in environment")
        return

    logger.info("Google Auth credentials fetched successfully")

    # 2️⃣ Create authenticated gspread client
    try:
        logger.info("Attempting to create gspread client")
        client = create_gspread_client(credentials_path)
        logger.info("gspread client created successfully")
    except Exception as e:
        logger.critical("Failed to create gspread client")
        logger.exception(e)
        return

    # 3️⃣ Initialize OrderCountersReader
    reader = OrderCountersReader(client)

    # 4️⃣ Fetch order counters from the live Google Sheet
    try:
        order_counters = reader.fetch_order_counters()
        if not order_counters:
            logger.warning("No valid order counters found in sheet")
        else:
            logger.info(f"{len(order_counters)} order counters fetched successfully")
            print("\n--- Live Order Counters ---")
            for college_code, data in order_counters.items():
                print(f" - {college_code}: last_order_number={data['last_order_number']}, updated_at={data['updated_at']}")
    except RuntimeError as e:
        logger.error("Error fetching order counters:")
        logger.error(e)
    except Exception as e:
        logger.error("Unexpected error occurred while fetching order counters:")
        logger.exception(e)

if __name__ == "__main__":
    main()
