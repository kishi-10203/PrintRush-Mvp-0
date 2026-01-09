from datetime import datetime, timezone
from typing import Dict, List
import gspread


class OrderIdGeneratorError(Exception):
    pass

class OrderIdGenerator:
    """
    Order ID format: {college}{YY}{sequence:04d}
    Example: HITS250001
    """

    def __init__(self, spreadsheet, counters_sheet_name="order_counters"):
        self.sheet = spreadsheet.worksheet(counters_sheet_name)
        self._counter_map: Dict[str, int] = {}
        self._row_map: Dict[str, int] = {}

    # 1️⃣ Load counters ONCE per batch
    def load_counters(self, college_codes: List[str]) -> None:
        records = self.sheet.get_all_records()

        for idx, row in enumerate(records, start=2):
            college = row["college_code"]
            if college in college_codes:
                self._counter_map[college] = row.get("last_order_number", 0) or 0
                self._row_map[college] = idx

        missing = set(college_codes) - self._counter_map.keys()
        if missing:
            raise OrderIdGeneratorError(
                f"College(s) not registered in order_counters: {', '.join(missing)}. "
                "System admin must add them."
            )

    # 2️⃣ Generate order_id using Order.created_at
    def generate_order_id(self, order) -> str:
        if order.college_code not in self._counter_map:
            raise OrderIdGeneratorError(
                f"Counter not loaded for college '{order.college_code}'"
            )

        if not order.created_at:
            raise OrderIdGeneratorError(
                "Order.created_at is required to generate order_id"
            )

        year_suffix = order.created_at.year % 100

        self._counter_map[order.college_code] += 1
        seq = self._counter_map[order.college_code]

        return f"{order.college_code}{year_suffix:02d}{seq:04d}"

    # 3️⃣ Commit counters ONCE
    def commit(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        updates = []

        for college, counter in self._counter_map.items():
            row = self._row_map[college]
            updates.append({
                "range": f"B{row}:C{row}",
                "values": [[counter, now]]
            })

        if updates:
            self.sheet.batch_update(updates)
