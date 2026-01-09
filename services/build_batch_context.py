from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from typing import Dict, Any
from types import MappingProxyType
import os

# dataclass imports
from models.batch_context import BatchContext
from config.static_config import GOOGLE_SHEETS_CONSTANTS, NOTION_CONSTANTS, WHATSAPP_CONSTANTS


# Indian Standard Time (IST) timezone
IST = timezone(timedelta(hours=5, minutes=30))



def generate_execution_id(now: datetime) -> str:
    """
    Generates a human-readable execution batch ID.
    Used ONLY for observability and logging.
    """
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    return f"EXEC-{timestamp}-IST"



def load_environment() -> Dict[str, str]:
    """
    Loads and validates required environment variables.
    Secrets only. No identifiers.
    """
    load_dotenv()

    env = {
        "NOTION_API_TOKEN": os.getenv("NOTION_API_TOKEN"),
        "GOOGLE_SHEETS_CREDENTIALS_PATH": os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH"),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID"),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN"),
        "TWILIO_WHATSAPP_FROM": os.getenv("TWILIO_WHATSAPP_FROM"),
    }

    missing = [key for key, value in env.items() if not value]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {missing}"
        )

    return env



""" ------ BATCH CONTEXT FACTORY ------"""

def build_batch_context(
    *,
    sheets_markers_reader,
    sheets_order_counter_reader,
    google_sheets_constants: Dict[str, Any],
    notion_constants: Dict[str, Any],
    whatsapp_constants: Dict[str, Any],
) -> BatchContext:
    """
    Cold-start bootstrap function.

    Responsibilities:
    - Load environment (read-only)
    - Generate execution metadata
    - Load static constants
    - Fetch high-water marks
    - Fetch college-wise counters

    Returns:
    - Immutable BatchContext snapshot
    """

    # ---- Environment ----
    env = MappingProxyType(load_environment())

    # ---- Execution metadata ----
    batch_start_time = datetime.now(IST)
    execution_id = generate_execution_id(batch_start_time)

    # ---- Constants (read-only identifiers) ----
    constants = MappingProxyType({
        "google_sheets": MappingProxyType(google_sheets_constants),
        "notion": MappingProxyType(notion_constants),
        "whatsapp": MappingProxyType(whatsapp_constants),
    })
    # ---- Metadata markers ----
    markers = MappingProxyType(sheets_markers_reader.fetch_markers())
    # Expected keys:
    # - last_processed_form_response_row
    # - last_notion_synced_row
    # - last_whatsapp_notification_sent_row

    # ---- College-wise order counters ----
    order_counters = MappingProxyType(sheets_order_counter_reader.fetch_counters())
    # Example: { "HITS": 124, "VIT": 87 }

    return BatchContext(
        execution_id=execution_id,
        batch_start_time=batch_start_time,
        timezone="IST",
        env=env,
        constants=constants,
        markers=markers,
        order_counters=order_counters,
    )