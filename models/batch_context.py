from dataclasses import dataclass
from datetime import datetime
from typing import Any
from types import MappingProxyType


@dataclass(frozen=True)
class BatchContext:
    """
    Immutable snapshot of system state at script start.
    This object MUST NOT be mutated downstream.
    """

    # --- Batch metadata ---
    batch_id: str
    batch_start_time: datetime
    timezone: str  # Locked to "IST" by convention

    # --- Environment / secrets ---
    # env: MappingProxyType[str, str | None]

    # --- Static constants ---
    constants: MappingProxyType[str, MappingProxyType[str, Any]]

    # --- High-water marks ---
    markers: MappingProxyType[str, int]

    # --- Order counters ---
    order_counters: MappingProxyType[str, int]