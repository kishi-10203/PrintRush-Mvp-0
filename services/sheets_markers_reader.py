from typing import Dict, List
from gspread import Client
from config.static_config import SHEETS_MARKERS_KEYS, GOOGLE_SHEETS_CONSTANTS


class SheetsMarkersReader:
    """
    Reads batch metadata (high-water marks) from Google Sheets.

    MVP0 constraints:
    - Read-only
    - Stateless
    - Deterministic
    """

    def __init__(self, sheets_service: Client):
        self.sheets_service = sheets_service
        self.spreadsheet_id = GOOGLE_SHEETS_CONSTANTS["MASTER_SPREAD_SHEET_ID"]
        self.sheet_name = GOOGLE_SHEETS_CONSTANTS["MARKERS_SHEET"]

    def fetch_markers(self) -> Dict[str, int]:
        """
        Reads the metadata sheet and returns last processed row numbers.
        Raises RuntimeError if any marker is missing or invalid.
        """
        #testing
        print("fetch markers called sucessfully")
        spreadsheet = self.sheets_service.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)

        data = sheet.get_all_values()
        #testing
        print(f"data fetched sucessfully \n {data}")

        if not data:
            raise RuntimeError(f"Markers sheet '{self.sheet_name}' is empty")

        markers: Dict[str, int] = {}
        invalid_keys: List[str] = []

        for row in data:
            # Skip rows without at least key-value
            if len(row) < 2:
                continue

            key = row[0].strip()
            value = row[1].strip()

            # Skip unknown keys
            if key not in SHEETS_MARKERS_KEYS:
                continue

            # Collect empty or non-integer values
            if not value:
                invalid_keys.append(key)
                continue

            try:
                markers[key] = int(value)
            except ValueError:
                invalid_keys.append(key)

        # Aggregate validation
        expected_keys = set(SHEETS_MARKERS_KEYS)
        found_keys = set(markers.keys())
        missing_keys = expected_keys - found_keys
        all_invalid_keys = sorted(set(invalid_keys) | missing_keys)


        if all_invalid_keys:
            raise RuntimeError(
                f"Invalid or missing marker values for keys: {all_invalid_keys} "
                f"from Google Sheet '{self.sheet_name}'"
            )

        return markers
