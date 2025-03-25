import logging
from datetime import datetime

from src.chunk.application.services.feed import FeedService
from src.chunk.infra.payload import ChunkPayload
from src.chunk.infra.processor import ChunkProcessor
from src.chunk.infra.storage import AWSOperator, MetadataOperator, PostgresOperator
from src.chunk.main.config import get_db_pool, get_s3_session
from src.chunk.main.constants import VALID_TABLES
from src.chunk.main.settings import get_settings


async def run():
    """
    Executes the main asynchronous workflow for data processing and operations.
    """
    settings = get_settings()
    logging.basicConfig(level=settings.log_level, format=settings.log_format)
    logger = logging.getLogger(__name__)

    pool = await get_db_pool(dsn=settings.dsn)
    session = get_s3_session(
        access_key_id=settings.aws_access_key_id,
        secret_access_key=settings.aws_secret_access_key,
        region=settings.aws_region,
    )
    fetch_operator = PostgresOperator(pool=pool)
    payload_operator = ChunkPayload()
    upload_operator = AWSOperator(session=session, bucket=settings.aws_bucket)
    processor = ChunkProcessor(
        settings=settings, pool=pool, storage=fetch_operator, payload=payload_operator, saver=upload_operator
    )
    metadata = MetadataOperator(session=session, bucket=settings.aws_bucket)
    service = FeedService(settings=settings, pool=pool, processor=processor, metadata=metadata)
    if settings.db_table_name not in VALID_TABLES:
        raise ValueError(f"Invalid table name: {settings.table}")
    start = datetime.now()
    logger.info("service.run: Starting processing")
    await service.feed()
    await pool.close()
    logger.debug(f"service.run: Processing finished in {(datetime.now() - start).total_seconds()} seconds")
    logger.info("service.run: Processing was finished")
