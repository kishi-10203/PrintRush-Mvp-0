
import logging
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any



class LoggerService:
    """
    Owns the logging lifecycle.
    Starts in bootstrap mode.
    Can be promoted to batch mode once BatchContext exists.
    """

    def __init__(self):
        self.logger = logging.getLogger("PrintRush")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        self._clear_handlers()
        self._init_bootstrap_logger()

    # -------------------------
    # Bootstrap Phase
    # -------------------------

    def _init_bootstrap_logger(self):
        os.makedirs("logs/bootstrap", exist_ok=True)

        handler = logging.FileHandler("logs/bootstrap/startup.log", encoding="utf-8")
        handler.setFormatter(self._json_formatter())

        self.logger.addHandler(handler)

        self._log_internal(
            level="INFO",
            service="system",
            event="bootstrap_logger_initialized",
            payload={}
        )