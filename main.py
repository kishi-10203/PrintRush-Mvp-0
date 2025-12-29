from models.order import Order
from handlers.notion_handler import create_order
from datetime import datetime, date

order = Order(
    order_id="TEST003",
    created_at=datetime.now(),
    college_code="SSN",
    college_name="Shiv nadar university",
    customer_name="Test User",
    whatsapp_number="9999999999",
    delivery_date=date.today(),
    delivery_slot="Morning : 8:30–10:00 AM",
    delivery_batch_id = "SSN-29122005-01",
    late_night_order=False,
    copies=3,
    pdf_file_url="http://example.com/test002.pdf",
    binding_type="Soft",
    total_pages_per_copy=23,
    special_instructions="Handle with care",
    color_pages_list="1,4,6,7,10",
    has_transparent_sheet=True,
    bonafied_page_count_per_copy=1,
    monochrome_pages_count_per_copy=18,
    color_pages_count_per_copy=5,
    glossy_front_page_count_per_copy=1,
    per_copy_total=161,
    order_total=483,
    whatsapp_sent=True,
)

page_id = create_order(order)
print("Created Notion page:", page_id)



#Afternoon: 12:00–1:30 PM   Morning : 8:30–10:00 AM