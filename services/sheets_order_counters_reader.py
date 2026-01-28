from typing import Dict, Any, List
from gspread import Client
from datetime import datetime

from config.static_config import GOOGLE_SHEETS_CONSTANTS , SHEETS_COUNTERS_KEYS

#logger imports
from models.system_logger import ETLLogger

etl_logger = ETLLogger()
logger = etl_logger.get_logger(file=__file__)


class OrderCountersReader:
    """
    Reads order counters from a Google Sheet.

    Sheet format:
    - college_code (str)
    - last_order_number (int)
    - updated_at (timestamp string)
    
    Validation:
    - last_order_number must be an integer
    - college_code cannot be empty
    """

    def __init__(self, sheets_service: Client):
        self.sheets_service = sheets_service
        self.spreadsheet_id = GOOGLE_SHEETS_CONSTANTS["MASTER_SPREAD_SHEET_ID"]
        self.sheet_name = GOOGLE_SHEETS_CONSTANTS["ORDER_COUNTERS_SHEET"]

    def fetch_order_counters(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetches and validates order counters from the sheet.
        Returns a dict:
        {
            "college_code1": {"last_order_number": 123, "updated_at": "2026-01-23 12:00:00"},
            "college_code2": {...},
        }
        """
        logger.info("Attempting to fetch order counters from Google Sheets")

        spreadsheet = self.sheets_service.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)
        data = sheet.get_all_values()
        logger.debug(f"Data fetched successfully, {len(data)} rows found")

        if not data:
            logger.critical(f"Order counters sheet '{self.sheet_name}' is empty")
            raise RuntimeError(f"Order counters sheet '{self.sheet_name}' is empty")

        counters: Dict[str, Dict[str, Any]] = {}
        invalid_rows: List[int] = []

        for idx, row in enumerate(data, start=1):
            if len(row) < 2:
                logger.warning(f"Row {idx} incomplete: {row} -- skipping")
                invalid_rows.append(idx)
                continue

            college_code = row[0].strip()
            last_order_number = row[1].strip()
            updated_at = row[2].strip() if len(row) >= 3 else None

            if not college_code:
                logger.warning(f"Row {idx} has empty college_code -- skipping")
                invalid_rows.append(idx)
                continue

            try:
                last_order_number_int = int(last_order_number)
            except ValueError:
                invalid_rows.append(idx)
                continue

            # Optional: validate timestamp format
            if updated_at:
                try:
                    # Adjust format to your sheet's timestamp format
                    datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    logger.warning(f"Row {idx} updated_at invalid: '{updated_at}' -- ignoring timestamp")
                    updated_at = None

            counters[college_code] = {
                "last_order_number": last_order_number_int,
                "updated_at": updated_at
            }

        if invalid_rows:
            pass
            #logger.warning(f"Invalid rows detected in sheet: {invalid_rows}")
            # Depending on policy, you can either raise an error or just skip invalid rows
            # raise RuntimeError(f"Invalid rows in sheet '{self.sheet_name}': {invalid_rows}")

        logger.info(f"Order counters fetched and validated successfully, {len(counters)} valid entries")
        return counters
