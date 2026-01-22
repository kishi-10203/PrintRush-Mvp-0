from datetime import datetime, timezone, timedelta

#logger imports
from models.system_logger import ETLLogger

etl_logger = ETLLogger()
logger = etl_logger.get_logger(file=__file__)



def batch_id_generator(now: datetime) -> str:
    """
    Generates a human-readable execution batch ID.
    Used ONLY for observability and logging.
    """
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    batch_id = f"EXEC-{timestamp}-IST"
    logger.info(f"Generated Batch ID: {batch_id}")

    return batch_id