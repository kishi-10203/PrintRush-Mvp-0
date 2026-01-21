from models.system_logger import ETLLogger
from config.logs_config import LOGGING_CONSTANTS

# Initialize the central logger
etl_logger = ETLLogger()

# Get module-level loggers
logger = etl_logger.get_logger(file=__file__)

# Emit some logs (console only)
logger.debug("Starting extraction (DEBUG)")
logger.info("Reading source data (INFO)")

print("\n✅ Console logs should appear above, in HH:MM:SS:MS format with module and level info.")
