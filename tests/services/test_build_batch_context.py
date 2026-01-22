import pytest
from datetime import datetime
from services.build_batch_context import build_batch_context, IST
from models.batch_context import BatchContext
from config.static_config import GOOGLE_SHEETS_CONSTANTS, NOTION_CONSTANTS, WHATSAPP_CONSTANTS

# ----------------------------
# Mock readers
# ----------------------------
class MockSheetsMetadataReader:
    def fetch_markers(self):
        return {
            "last_processed_form_response_row": 10,
            "last_notion_synced_row": 8,
            "last_whatsapp_notification_sent_row": 5,
        }

class MockSheetsOrderCounterReader:
    def fetch_counters(self):
        return {
            "HITS": 123,
            "VIT": 87,
        }

# ----------------------------
#  constants
# ----------------------------
GOOGLE_SHEETS_CONSTANTS = GOOGLE_SHEETS_CONSTANTS
NOTION_CONSTANTS = NOTION_CONSTANTS
WHATSAPP_CONSTANTS = WHATSAPP_CONSTANTS

# ----------------------------
# Pytest fixtures
# ----------------------------
@pytest.fixture
def mock_readers():
    return MockSheetsMetadataReader(), MockSheetsOrderCounterReader()

# ----------------------------
# Test cases
# ----------------------------
def test_build_batch_context_structure(mock_readers):
    markers_reader, counter_reader = mock_readers

    ctx: BatchContext = build_batch_context(
        sheets_markers_reader=markers_reader,
        sheets_order_counter_reader=counter_reader,
        google_sheets_constants=GOOGLE_SHEETS_CONSTANTS,
        notion_constants=NOTION_CONSTANTS,
        whatsapp_constants=WHATSAPP_CONSTANTS,
    )

    # --- Type checks ---
    assert isinstance(ctx, BatchContext)
    assert isinstance(ctx.batch_id, str)
    assert isinstance(ctx.batch_start_time, datetime)
    assert ctx.timezone == "IST"

    # --- Environment ---
    env_keys = [
        "NOTION_API_TOKEN",
        "GOOGLE_SHEETS_CREDENTIALS_PATH",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_FROM",
    ]
    for key in env_keys:
        # Value can be None if .env not loaded in test; just check key presence
        assert key in ctx.env

    # --- Constants ---
    for k in ["google_sheets", "notion", "whatsapp"]:
        assert k in ctx.constants

    # --- Markers ---
    markers = ctx.markers
    for key in [
        "last_processed_form_response_row",
        "last_notion_synced_row",
        "last_whatsapp_notification_sent_row",
    ]:
        assert key in markers

    # --- Order counters ---
    counters = ctx.order_counters
    assert counters.get("HITS") == 123
    assert counters.get("VIT") == 87


def test_batch_context_immutable(mock_readers):
    markers_reader, counter_reader = mock_readers
    ctx: BatchContext = build_batch_context(
        sheets_markers_reader=markers_reader,
        sheets_order_counter_reader=counter_reader,
        google_sheets_constants=GOOGLE_SHEETS_CONSTANTS,
        notion_constants=NOTION_CONSTANTS,
        whatsapp_constants=WHATSAPP_CONSTANTS,
    )

    # Attempting mutation should raise TypeError (for frozen dataclass and MappingProxyType)
    from dataclasses import FrozenInstanceError
    with pytest.raises((TypeError, FrozenInstanceError)):
        ctx.batch_id = "NEW_EXEC_ID"

    with pytest.raises((TypeError, FrozenInstanceError)):
        ctx.markers["last_processed_form_response_row"] = 999


def test_batch_id_format(mock_readers):
    markers_reader, counter_reader = mock_readers
    ctx: BatchContext = build_batch_context(
        sheets_markers_reader=markers_reader,
        sheets_order_counter_reader=counter_reader,
        google_sheets_constants=GOOGLE_SHEETS_CONSTANTS,
        notion_constants=NOTION_CONSTANTS,
        whatsapp_constants=WHATSAPP_CONSTANTS,
    )

    # Must start with "EXEC-" and end with "-IST"
    assert ctx.batch_id.startswith("EXEC-")
    assert ctx.batch_id.endswith("-IST")
