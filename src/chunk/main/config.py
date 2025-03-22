import logging

import asyncpg
from aioboto3.session import Session

logger = logging.getLogger(__name__)


async def get_db_pool(dsn: str) -> asyncpg.Pool:
    """Create and return a connection pool."""
    logger.debug(f"get_db_pool: Creating connection pool with DSN: {dsn}")
    return await asyncpg.create_pool(dsn=dsn)


def get_s3_session(access_key_id: str, secret_access_key: str, region: str) -> Session:
    """
    Creates and returns a new AWS S3 session using the provided credentials and region.
    """
    return Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, region_name=region)
