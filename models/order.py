# order.py
from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime


@dataclass
class Order:
    # Identity
    order_id: str
    created_at: Optional[datetime] = None

    # College
    college_code: Optional[str] = None
    college_name: Optional[str] = None

    # Customer
    customer_name: Optional[str] = None
    whatsapp_number: Optional[str] = None

    # Delivery
    delivery_date: Optional[date] = None
    delivery_slot: Optional[str] = None
    delivery_batch_id: Optional[str] = None
    late_night_order: bool = False

    # Print specs
    pdf_file_url: Optional[str] = None
    copies: Optional[int] = None
    binding_type: Optional[str] = None
    total_pages_per_copy: Optional[int] = None

    color_pages_list: Optional[str] = None
    color_pages_count_per_copy: Optional[int] = None
    monochrome_pages_count_per_copy: Optional[int] = None

    glossy_front_page_count_per_copy: Optional[int] = None
    bonafied_page_count_per_copy: Optional[int] = None

    has_transparent_sheet: bool = False
    full_report_in_bond_paper: bool = False

    # Pricing
    per_copy_total: Optional[float] = None
    order_total: Optional[float] = None

    # Ops / status
    order_status: str = "New"
    payment_status: str = "Pending"
    payment_mode: Optional[str] = None
    whatsapp_sent: bool = False
    special_instructions: Optional[str] = None
