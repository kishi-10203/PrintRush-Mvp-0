import logging
import re

import pytest

from models.system_logger import ETLLogger
from config.logs_config import LOGGING_CONSTANTS


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def reset_etl_logger():
    """
    Ensure a clean logger state between tests.
    """
    app_logger = logging.getLogger(LOGGING_CONSTANTS["LOGGER_NAME"])
    for handler in list(app_logger.handlers):
        app_logger.removeHandler(handler)
        handler.close()
    app_logger.setLevel(logging.NOTSET)
    app_logger.propagate = True
    ETLLogger._initialized = False


@pytest.fixture(autouse=True)
def clean_logger_state():
    reset_etl_logger()
    yield
    reset_etl_logger()


# ----------------------------------------------------------------------
# Tests: Console Handler
# ----------------------------------------------------------------------

def test_console_handler_configured_once():
    ETLLogger()
    ETLLogger()  # second init should not add another handler

    app_logger = logging.getLogger(LOGGING_CONSTANTS["LOGGER_NAME"])
    handlers = app_logger.handlers

    console_handlers = [
        h for h in handlers if isinstance(h, logging.StreamHandler)
    ]

    assert len(console_handlers) == 1
    assert console_handlers[0].level == logging.DEBUG
    assert app_logger.propagate is False


def test_console_logs_debug(capsys):
    logger_mgr = ETLLogger()
    logger = logger_mgr.get_logger(LOGGING_CONSTANTS["LOGGER_NAME"])

    logger.debug("debug message")

    output = capsys.readouterr().out
    assert "debug message" in output



def test_console_timestamp_time_only(capsys):
    logger_mgr = ETLLogger()
    logger = logger_mgr.get_logger(LOGGING_CONSTANTS["LOGGER_NAME"])

    # Log a message that should appear in the console
    logger.info("time check")

    # Capture what was printed to console
    output = capsys.readouterr().out.strip()

    # HH:MM:SS.mmm at the beginning (milliseconds included)
    assert re.match(r"\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?", output)

    # Ensure no date (YYYY-MM-DD)
    assert not re.search(r"\d{4}-\d{2}-\d{2}", output)

    # Also ensure the message appears
    assert "time check" in output


# ----------------------------------------------------------------------
# Tests: Batch File Handler
# ----------------------------------------------------------------------

def test_batch_file_created(tmp_path):
    logger_mgr = ETLLogger(log_dir=tmp_path)

    batch_id = "batch_001"
    logger_mgr.start_batch(batch_id)

    log_file = tmp_path / f"{batch_id}.log"
    assert log_file.exists()

    logger_mgr.end_batch()


def test_batch_file_logs_info_not_debug(tmp_path):
    logger_mgr = ETLLogger(log_dir=tmp_path)
    logger = logger_mgr.get_logger(LOGGING_CONSTANTS["LOGGER_NAME"])

    batch_id = "batch_002"
    logger_mgr.start_batch(batch_id)

    logger.debug("debug should not appear")
    logger.info("info should appear")

    logger_mgr.end_batch()

    content = (tmp_path / f"{batch_id}.log").read_text()

    assert "info should appear" in content
    assert "debug should not appear" not in content


def test_batch_file_timestamp_full(tmp_path):
    logger_mgr = ETLLogger(log_dir=tmp_path)
    logger = logger_mgr.get_logger(LOGGING_CONSTANTS["LOGGER_NAME"])

    batch_id = "batch_003"
    logger_mgr.start_batch(batch_id)

    logger.info("timestamp check")

    logger_mgr.end_batch()

    content = (tmp_path / f"{batch_id}.log").read_text().strip()

    # Expect YYYY-MM-DD at the beginning
    assert re.match(r"\d{4}-\d{2}-\d{2}", content)


def test_batch_handler_removed_after_end_batch():
    logger_mgr = ETLLogger()
    app_logger = logging.getLogger(LOGGING_CONSTANTS["LOGGER_NAME"])

    initial_handler_count = len(app_logger.handlers)

    logger_mgr.start_batch("batch_004")
    assert len(app_logger.handlers) == initial_handler_count + 1

    logger_mgr.end_batch()
    assert len(app_logger.handlers) == initial_handler_count


# ----------------------------------------------------------------------
# Tests: Logger Hierarchy
# ----------------------------------------------------------------------

def test_child_logger_inherits_handlers(capsys):
    logger_mgr = ETLLogger()
    logger = logger_mgr.get_logger(LOGGING_CONSTANTS["LOGGER_NAME"] + ".load")
    logger.info("child logger message")

    output = capsys.readouterr().out.strip()

    assert f"{LOGGING_CONSTANTS['LOGGER_NAME']}.load" in output
    assert "child logger message" in output