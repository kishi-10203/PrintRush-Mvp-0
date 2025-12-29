# handlers/notion_handler.py

import os
import requests
from dotenv import load_dotenv
from models.order import Order
from exceptions import NotionHandlerError

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_ORDER_DATABASE_ID")
NOTION_VERSION = os.getenv("NOTION_VERSION")

NOTION_API_URL = "https://api.notion.com/v1/pages"


def _build_properties(order: Order) -> dict:
    """Convert Order object to Notion properties payload"""

    props = {
        "order_id": {
            "title": [{"text": {"content": order.order_id}}]
        },
        "order_status": {
            "select": {"name": order.order_status}
        },
        "payment_status": {
            "select": {"name": order.payment_status}
        },
        "whatsapp_sent": {
            "checkbox": order.whatsapp_sent
        }
    }

    # Helper functions
    def text(val):
        return {"rich_text": [{"text": {"content": val}}]} if val else None

    def number(val):
        return {"number": val} if val is not None else None

    def select(val):
        return {"select": {"name": val}} if val else None

    def checkbox(val):
        return {"checkbox": val} if val is not None else None

    def date(val):
        return {"date": {"start": val.isoformat()}} if val else None

    def url(val):
        return {"url": val} if val else None

    mapping = {
        "created_at": date(order.created_at),
        "college_code": select(order.college_code),
        "college_name": text(order.college_name),
        "customer_name": text(order.customer_name),
        "whatsapp_number": {"phone_number": order.whatsapp_number} if order.whatsapp_number else None,
        "delivery_date": date(order.delivery_date),
        "delivery_slot": select(order.delivery_slot),
        "delivery_batch_id": text(order.delivery_batch_id),
        "late_night_order": checkbox(order.late_night_order),
        "pdf_file_url": url(order.pdf_file_url),
        "copies": number(order.copies),
        "binding_type": select(order.binding_type),
        "total_pages_per_copy": number(order.total_pages_per_copy),
        "color_pages_list": text(order.color_pages_list),
        "color_pages_count_per_copy": number(order.color_pages_count_per_copy),
        "monochrome_pages_count_per_copy": number(order.monochrome_pages_count_per_copy),
        "glossy_front_page_count_per_copy": number(order.glossy_front_page_count_per_copy),
        "bonafied_page_count_per_copy": number(order.bonafied_page_count_per_copy),
        "has_transparent_sheet": checkbox(order.has_transparent_sheet),
        "full_report_in_bond_paper": checkbox(order.full_report_in_bond_paper),
        "per_copy_total": number(order.per_copy_total),
        "order_total": number(order.order_total),
        "special_instructions": text(order.special_instructions),
        "payment_mode": select(order.payment_mode),
    }

    # Add only non-null properties
    for key, value in mapping.items():
        if value is not None:
            props[key] = value

    return props


def create_order(order: Order) -> str:
    """Create a new order in Notion. Returns page_id."""

    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        raise NotionHandlerError("Notion credentials not set")

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": _build_properties(order),
    }

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    response = requests.post(
        NOTION_API_URL,
        headers=headers,
        json=payload,
        timeout=10,
    )

    if response.status_code != 200:
        raise NotionHandlerError(
            f"Notion API error {response.status_code}: {response.text}"
        )

    return response.json()["id"]
