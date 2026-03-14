from typing import List, Dict
from gspread import Client

from models.batch_context import BatchContext
from models.system_logger import ETLLogger


etl_logger = ETLLogger()
logger = etl_logger.get_logger(file=__file__)




class RawOrderFetchingService:
    """
    Fetches new raw orders from Google Sheets using BatchContext markers.

    MVP0 constraints:
    - Read-only
    - Stateless
    - Deterministic
    - Does NOT mutate markers
    """

    def __init__(self, sheets_service: Client, batch_context: BatchContext):
        self.sheets_service = sheets_service
        self.batch_context = batch_context

        # All configuration must come from BatchContext
        self.spreadsheet_id = batch_context.google_sheets_config[
            "MASTER_SPREAD_SHEET_ID"
        ]
        self.sheet_name = batch_context.google_sheets_config[
            "RAW_ORDERS_SHEET"
        ]



    def fetch_new_orders(self) -> List[Dict[str, str]]:
        """
        Returns only rows that appear AFTER the last_processed_form_response marker.
        Raises RuntimeError if sheet header is invalid.
        """

        logger.info(
            f"[Execution ID: {self.batch_context.execution_id}] "
            "Fetching raw orders from Google Sheets"
        )

        last_processed_row = self.batch_context.markers[
            "last_processed_form_response"
        ]

        spreadsheet = self.sheets_service.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)

        # Fetch header (Row 1)
        header = sheet.row_values(1)

        if not header:
            logger.critical(
                "Raw orders header sheet is empty - no headers found."
            )
            raise RuntimeError("Raw orders sheet header is empty")

        start_row = last_processed_row + 1

        logger.info(
            f"Fetching raw orders from row {start_row} onward | "
            f"Last processed marker: {last_processed_row}"
        )

        # Fetch only new rows (delta-based incremental ingestion)
        new_rows = sheet.get(f"A{start_row}:Z")

        if not new_rows:
            logger.info("No new raw orders found")
            return []

        structured_orders: List[Dict[str, str]] = []

        for row in new_rows:
            # Skip fully empty rows
            if not any(cell.strip() for cell in row):
                continue

            # Ensure row matches header length
            padded_row = row + [""] * (len(header) - len(row))

            structured_orders.append(dict(zip(header, padded_row)))

        logger.info(
            f"Fetched {len(structured_orders)} new raw orders "
            f"(Execution ID: {self.batch_context.execution_id})"
        )

        return structured_orders
