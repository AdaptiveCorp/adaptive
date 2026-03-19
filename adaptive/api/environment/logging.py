import logging
import sys

from adaptive.api.environment.config import settings


def setup_logging() -> None:
    """Configure the 'adaptive' logger from settings."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )

    root = logging.getLogger("adaptive")
    root.setLevel(level)
    root.addHandler(handler)

    # Reduce noise from chatty libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("ansible_runner").setLevel(logging.WARNING)
