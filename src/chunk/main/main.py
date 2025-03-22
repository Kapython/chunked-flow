import asyncio
import sys
from pathlib import Path

sys.path.append(Path().cwd().__str__())

from src.chunk.presentation.service import run


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
