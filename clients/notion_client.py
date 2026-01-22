import os
import time
import requests
from dotenv import load_dotenv
from exceptions import NotionHandlerError

from models.system_logger import ETLLogger


etl_logger = ETLLogger()
logger = etl_logger.get_logger(file=__file__)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_VERSION = os.getenv("NOTION_VERSION")
NOTION_API_URL = "https://api.notion.com/v1/pages"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


def create_page(payload: dict, retries: int = 3) -> dict:
    if not NOTION_TOKEN:
        raise NotionHandlerError("Notion token not set")

    for attempt in range(retries):
        response = requests.post(
            NOTION_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()

        # Retry on rate limit or transient failures
        if response.status_code in (429, 500, 502, 503):
            time.sleep(2 ** attempt)
            continue

        raise NotionHandlerError(
            f"Notion API error {response.status_code}: {response.text}"
        )

    raise NotionHandlerError("Notion API retries exhausted")
