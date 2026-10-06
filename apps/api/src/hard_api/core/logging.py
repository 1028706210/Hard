from __future__ import annotations

import logging


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("hard_api")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    return logger
