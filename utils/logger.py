import logging
import os
from datetime import datetime


def setup_logger(name: str) -> logging.Logger:
    """
    Returns a named logger that writes to both:
    - Console (WARNING and above)
    - logs/snapclass.log (DEBUG and above)

    All loggers share the same file — separated by name prefix.
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers if setup_logger is called multiple times
    # (happens because Streamlit reruns the full script on every interaction)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Formatter ─────────────────────────────────────────────────────────────
    fmt = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── Console handler — WARNING and above only ──────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(fmt)

    # ── File handler — DEBUG and above, rotating by date ─────────────────────
    log_dir  = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "snapclass.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger