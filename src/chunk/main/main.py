import asyncio
import logging
import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.parent.parent.parent.as_posix())

from src.chunk.presentation.service import run

logger = logging.getLogger(__name__)


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("main: KeyboardInterrupt")


if __name__ == "__main__":
    main()
