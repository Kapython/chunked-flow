import asyncio
import json
import logging
import time

import asyncpg

from src.chunk.domain.facility.processor import Processor
from src.chunk.domain.facility.storage import Saver
from src.chunk.infra.storage import OffsetManager
from src.chunk.main.settings import Settings

logger = logging.getLogger(__name__)


class FeedService:
    pool: asyncpg.Pool
    processor: Processor
    metadata: Saver
    offset_manager: OffsetManager
    settings: Settings
    uploaded_files: list = []

    def __init__(self, settings: Settings, pool: asyncpg.Pool, processor: Processor, metadata: Saver):
        self.settings = settings
        self.pool = pool
        self.semaphore = asyncio.Semaphore(settings.concurrency_limit)
        self.processor = processor
        self.metadata = metadata
        self.offset_manager = OffsetManager(pool, settings.offset_initial)

    async def feed(self):
        """
        Fetches data incrementally by executing tasks in chunks and manages concurrency
        through a semaphore. This method continuously creates and executes an asynchronous
        task with an increasing offset, determined by the configured chunk size.
        """
        offset = await self.offset_manager.fetch_offset(self.settings.db_table_name)
        while True:
            logger.debug(f"FeedService.feed: Offset {offset} with size {self.settings.chunk_size}")
            task = asyncio.create_task(self.semaphore_wrapper(offset))
            success = await task
            if not success:
                logger.debug(f"FeedService.feed: Offset: {offset} was finished")
                break
            offset += self.settings.chunk_size
        timestamp = int(time.time())
        success = await self.metadata.save_data(
            data=self.create_metadata_file(timestamp=timestamp),
            file_name=self.settings.metadata_file_name.format(timestamp=timestamp),
        )
        if not success:
            logger.error(f"FeedService.feed: Failed to save metadata file {self.settings.metadata_file_name}")

    async def semaphore_wrapper(self, ofs):
        """
        Executes a function within an asynchronous semaphore context to limit concurrency.
        """
        async with self.semaphore:
            try:
                return await self.processor.handle(ofs, self.uploaded_files)
            except Exception as e:
                logger.error(f"Failed to process offset {ofs}: {e}")
                return False

    def create_metadata_file(self, timestamp: float) -> str:
        """Create a metadata file with the list of uploaded files."""
        metadata = {
            "generation_timestamp": timestamp,
            "name": "reservewithgoogle.entity",
            "data_file": self.uploaded_files,
        }
        logger.debug(f"FeedService.create_metadata_file: Metadata file: {metadata}")
        return json.dumps(metadata)
