import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("deed")

if not logger.handlers:
    logger.setLevel(logging.INFO)
    handlers = RotatingFileHandler(
        "logs.txt",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )

    handlers.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    ))
    logger.addHandler(handlers)