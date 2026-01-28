import logging
import sys
from pathlib import Path
from config.logs_config import LOGGING_CONSTANTS


class ETLLogger:
    """
    Central logging manager for the ETL pipeline.
    """

    _initialized = False

    def __init__(
        self,
        app_logger_name: str = LOGGING_CONSTANTS["LOGGER_NAME"],
        log_dir: str = Path(LOGGING_CONSTANTS["LOG_DIRECTORY"]),
    ):
        self.app_logger_name = app_logger_name
        self.log_dir = Path(log_dir)

        # Root logger for batch logging
        self._app_logger = logging.getLogger(self.app_logger_name)
        self._app_logger.setLevel(logging.DEBUG)
        self._app_logger.propagate = False

        self._file_handler = None

        if not ETLLogger._initialized:
            self._configure_base_logger()
            ETLLogger._initialized = True

    # ---------------------------
    # Base logger (console)
    # ---------------------------
    def _configure_base_logger(self):
        """
        Attach console handler to root logger for default logging.
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d - %(levelname)s  - %(name)s - %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)

        self._app_logger.addHandler(console_handler)

    # ---------------------------
    # Batch lifecycle
    # ---------------------------
    def start_batch(self, batch_id: str):
        """
        Start a new batch file for logging.
        """
        self.log_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.log_dir / f"{batch_id}.log"

        # Remove old handler if exists
        if self._file_handler:
            self.end_batch()

        self._file_handler = logging.FileHandler(log_path, mode="w")
        self._file_handler.setLevel(logging.INFO)

        file_formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self._file_handler.setFormatter(file_formatter)

        self._app_logger.addHandler(self._file_handler)

    def end_batch(self):
        """
        Close the current batch file handler.
        """
        if self._file_handler:
            self._app_logger.removeHandler(self._file_handler)
            self._file_handler.close()
            self._file_handler = None

    # ---------------------------
    # Public API: get module logger
    # ---------------------------
    def get_logger(self, module_name: str = None, file: str = None):
        """
        Return a logger for a module.

        Args:
            module_name (str, optional): Explicit module name.
            file (str, optional): __file__ of the calling module.
        """
        # Use file stem if provided
        if file is not None:
            module_name = Path(file).stem
        elif module_name is None:
            module_name = self.app_logger_name  # fallback

        # Handle __main__ scripts
        if module_name == "__main__" and file is not None:
            module_name = Path(file).stem

        logger = logging.getLogger(module_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True

        # Console handler (attach once)
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            import sys
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(
                fmt="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
                datefmt="%H:%M:%S",
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        return logger
