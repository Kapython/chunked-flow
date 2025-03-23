import logging
import time

import asyncpg

from src.chunk.domain.facility.payload import Payload
from src.chunk.domain.facility.processor import Processor
from src.chunk.domain.facility.storage import Fetcher, Saver
from src.chunk.main.settings import Settings

logger = logging.getLogger(__name__)


class ChunkProcessor(Processor):
    settings: Settings
    pool: asyncpg.Pool
    payload: Payload
    fetcher: Fetcher
    saver: Saver

    def __init__(self, settings, pool: asyncpg.Pool, payload: Payload, storage: Fetcher, saver: Saver):
        self.settings = settings
        self.pool = pool
        self.payload = payload
        self.fetcher = storage
        self.saver = saver

    async def handle(self, offset: int, uploaded_files: list):
        """Fetch a chunk from DB, transform, compress, and save."""
        logger.debug(f"ChunkProcessor.handle: Processing chunk {offset}")
        rows = await self.fetcher.fetch_data(offset, self.settings.chunk_size)
        if not rows:
            return False

        data_str = await self.payload.build_payload(rows)
        compressed_data = await self.payload.compress(data_str)

        timestamp = int(time.time())
        file_name = f"facility_feed_{timestamp}_{offset}.json.gz"
        logger.debug(f"ChunkProcessor.handle: File name - {file_name}")
        success = await self.saver.save_data(compressed_data, file_name)
        if not success:
            logger.error(f"ChunkProcessor.handle: Failed to save file {file_name}")
            return False
        uploaded_files.append(file_name)
        return True
