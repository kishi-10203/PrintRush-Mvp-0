import pytest
from unittest.mock import MagicMock

from services.sheets_markers_reader import SheetsMarkersReader
from config.static_config import SHEETS_MARKERS_KEYS


# -------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------

@pytest.fixture
def mock_gspread_client():
    """
    Mocked gspread Client → Spreadsheet → Worksheet chain.
    """
    client = MagicMock()
    spreadsheet = MagicMock()
    worksheet = MagicMock()

    client.open_by_key.return_value = spreadsheet
    spreadsheet.worksheet.return_value = worksheet

    return client, worksheet


def make_valid_marker_rows():
    """
    Helper: returns fully valid marker rows.
    """
    return [
        ["last_processed_form_response_row", "10"],
        ["last_notion_synced_row", "8"],
        ["last_whatsapp_notification_sent_row", "6"],
    ]


# -------------------------------------------------------------------
# Success Case
# -------------------------------------------------------------------

def test_fetch_markers_success_when_all_markers_present(mock_gspread_client):
    client, worksheet = mock_gspread_client
    worksheet.get_all_values.return_value = make_valid_marker_rows()

    reader = SheetsMarkersReader(client)
    markers = reader.fetch_markers()

    assert markers == {
        "last_processed_form_response_row": 10,
        "last_notion_synced_row": 8,
        "last_whatsapp_notification_sent_row": 6,
    }


# -------------------------------------------------------------------
# Failure Cases (Aggregated Validation)
# -------------------------------------------------------------------

def test_fetch_markers_raises_when_sheet_is_empty(mock_gspread_client):
    client, worksheet = mock_gspread_client
    worksheet.get_all_values.return_value = []

    reader = SheetsMarkersReader(client)

    with pytest.raises(RuntimeError, match="Markers sheet"):
        reader.fetch_markers()


def test_fetch_markers_raises_for_missing_keys(mock_gspread_client):
    client, worksheet = mock_gspread_client

    worksheet.get_all_values.return_value = [
        ["last_processed_form_response_row", "5"],
    ]

    reader = SheetsMarkersReader(client)

    with pytest.raises(RuntimeError) as exc:
        reader.fetch_markers()

    error_message = str(exc.value)

    # Assert all missing keys are reported
    for key in SHEETS_MARKERS_KEYS:
        if key != "last_processed_form_response_row":
            assert key in error_message


def test_fetch_markers_raises_for_empty_values(mock_gspread_client):
    client, worksheet = mock_gspread_client

    worksheet.get_all_values.return_value = [
        ["last_processed_form_response_row", ""],
        ["last_notion_synced_row", "5"],
        ["last_whatsapp_notification_sent_row", "3"],
    ]

    reader = SheetsMarkersReader(client)

    with pytest.raises(RuntimeError) as exc:
        reader.fetch_markers()

    assert "last_processed_form_response_row" in str(exc.value)


def test_fetch_markers_raises_for_non_integer_values(mock_gspread_client):
    client, worksheet = mock_gspread_client

    worksheet.get_all_values.return_value = [
        ["last_processed_form_response_row", "abc"],
        ["last_notion_synced_row", "5"],
        ["last_whatsapp_notification_sent_row", "3"],
    ]

    reader = SheetsMarkersReader(client)

    with pytest.raises(RuntimeError) as exc:
        reader.fetch_markers()

    assert "last_processed_form_response_row" in str(exc.value)


def test_fetch_markers_reports_multiple_invalid_keys_together(mock_gspread_client):
    client, worksheet = mock_gspread_client

    worksheet.get_all_values.return_value = [
        ["last_processed_form_response_row", ""],   # empty
        ["last_notion_synced_row", "xyz"],           # non-integer
        # missing last_whatsapp_notification_sent_row
    ]

    reader = SheetsMarkersReader(client)

    with pytest.raises(RuntimeError) as exc:
        reader.fetch_markers()

    error_message = str(exc.value)

    assert "last_processed_form_response_row" in error_message
    assert "last_notion_synced_row" in error_message
    assert "last_whatsapp_notification_sent_row" in error_message
