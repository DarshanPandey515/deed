import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("deed")

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
logger.info("service started")

logger.error("something went wrong")