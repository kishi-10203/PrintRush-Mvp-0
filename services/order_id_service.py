import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from exceptions import OrderCounterError

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_ORDER_COUNTERS_DB_ID = os.getenv("NOTION_ORDER_COUNTERS_DB_ID")
NOTION_VERSION = os.getenv("NOTION_VERSION")

NOTION_API_BASE = "https://api.notion.com/v1"


def _headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def generate_order_id(college_code: str) -> str:
    """
    Returns next order_id like HITS0001
    """

    # 1️⃣ Query counter row
    query_payload = {
        "filter": {
            "property": "college_code",
            "title": {
                "equals": college_code
            }
        }
    }

    resp = requests.post(
        f"{NOTION_API_BASE}/databases/{NOTION_ORDER_COUNTERS_DB_ID}/query",
        headers=_headers(),
        json=query_payload,
        timeout=10
    )

    if resp.status_code != 200:
        raise OrderCounterError(resp.text)

    results = resp.json()["results"]

    # College not registered → HARD FAIL
    if not results:
        raise OrderCounterError(
            f"College code '{college_code}' not registered in OrderCounters"
        )


    # 2️⃣ If college exists → increment
    if results:
        page = results[0]
        page_id = page["id"]

        last_inc = page["properties"]["last_counter"]["number"] or 0
        next_inc = last_inc + 1

        update_payload = {
            "properties": {
                "last_counter": {"number": next_inc},
                "updated_at": {
                    "date": {"start": datetime.utcnow().isoformat()}
                }
            }
        }

        update_resp = requests.patch(
            f"{NOTION_API_BASE}/pages/{page_id}",
            headers=_headers(),
            json=update_payload,
            timeout=10
        )

        if update_resp.status_code != 200:
            raise OrderCounterError(update_resp.text)


    # 4️⃣ Return formatted order ID
    return f"{college_code}{next_inc:04d}"