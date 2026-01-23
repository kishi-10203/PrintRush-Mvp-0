from datetime import datetime, timezone, timedelta

# ETL - Requirements Gathering Form Response Sheet Names
GOOGLE_SHEETS_CONSTANTS = {
    "MASTER_SPREAD_SHEET_NAME": "dev_rush_order_responses",
    "MASTER_SPREAD_SHEET_ID": "1avuUjR347Fa_Lhn3deOn1_F0BvXvYshWHqTFU_6WffU",
    "FORM_RESPONSE_SHEET": "form_responses",
    "PROCESSED_ORDERS_SHEET": "processed_orders",
    "MARKERS_SHEET": "last_batch_markers",
    "ORDER_COUNTERS_SHEET": "order_counters",
}


NOTION_CONSTANTS = {
    "DATABASE_NAME": "orders_database",
    "DATABASE_ID": "2d3ceca9c82180c994d6f0ff053c1109",
    "API_VERSION": "2025-09-03",
    "API_URL": "https://api.notion.com/v1",
}


WHATSAPP_CONSTANTS = {
    "MESSAGE_TEMPLATE_ID": "print_rush_order_update",
    "SENDER_NAME": "PrintRush",
}


# ETL - Sheets Markers Keys
SHEETS_MARKERS_KEYS = [
    'last_processed_form_response_row',
    'last_notion_synced_row',
    'last_whatsapp_notification_sent_row',
]

# ETL - Sheets Order Counters Keys
SHEETS_COUNTERS_KEYS = [
    'college_code',
    'last_order_number',
    'updated_at'
]

# Indian Standard Time (IST) timezone
IST = timezone(timedelta(hours=5, minutes=30))