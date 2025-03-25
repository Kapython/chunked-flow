import logging
from datetime import datetime

import asyncpg
from aioboto3.session import Session

from src.chunk.domain.facility.storage import Fetcher, Saver

logger = logging.getLogger(__name__)


class PostgresOperator(Fetcher):
    pool: asyncpg.Pool

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def fetch_data(self, offset: int, limit: int, table: str) -> list[dict]:
        """Fetch a chunk of facility records."""
        rows = await self.get_rows(offset, limit, table)
        logger.debug(f"PostgresOperator.fetch_data: {len(rows)} rows were fetched.")
        return [dict(row) for row in rows]

    async def get_rows(self, offset: int, limit: int, table: str):
        """
        Fetches a paginated list of records from the database.
        """
        start = datetime.now()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"SELECT * FROM {table} WHERE id > $1 ORDER BY id LIMIT $2", offset, limit)  # noqa S608
        logger.debug(
            f"PostgresOperator.get_rows: {len(rows)} rows were fetched."
            f" Offset: {offset}. Chunk {limit}. Time: {(datetime.now() - start).total_seconds()}"
        )
        return rows


class AWSOperator(Saver):
    session: Session
    bucket: str
    success_http_code: int = 200

    def __init__(self, session: Session, bucket: str):
        self.session = session
        self.bucket = bucket

    async def save_data(self, data: bytes | str, file_name: str) -> bool:
        """Uploads gzip data to S3 asynchronously."""
        start = datetime.now()
        async with self.session.client("s3") as s3_client:
            res = await s3_client.put_object(
                Bucket=self.bucket, Key=file_name, Body=data, ContentType="application/json", ContentEncoding="gzip"
            )
        logger.debug(
            f"AWSOperator.save_data: File {file_name} uploaded to S3. Time: {(datetime.now() - start).total_seconds()}"
        )
        status = res.get("ResponseMetadata", {}).get("HTTPStatusCode", False)
        return status == self.success_http_code


class MetadataOperator(Saver):
    session: Session
    bucket: str
    success_http_code: int = 200

    def __init__(self, session: Session, bucket: str):
        self.session = session
        self.bucket = bucket

    async def save_data(self, data: bytes | str, file_name: str) -> bool:
        """Uploads data to S3 asynchronously."""

        start = datetime.now()
        async with self.session.client("s3") as s3_client:
            res = await s3_client.put_object(
                Bucket=self.bucket,
                Key=file_name,
                Body=data,
                ContentType="application/json",
            )
        logger.debug(
            f"MetadataOperator.save_data: Metadata file {file_name} uploaded to S3. "
            f"Time: {(datetime.now() - start).total_seconds()}"
        )
        status = res.get("ResponseMetadata", {}).get("HTTPStatusCode", False)
        return status == self.success_http_code


class OffsetManager:
    offset: int | None = None
    pool: asyncpg.Pool

    def __init__(self, pool: asyncpg.Pool, offset: int | None = None):
        self.pool = pool
        self.offset = offset

    async def fetch_offset(self, table: str) -> int:
        """
        Fetches the minimum offset value from the database or returns the pre-existing offset.
        """
        if self.offset:
            return self.offset
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(f"SELECT MIN(id) FROM {table}")  # noqa S608
        offset = row[0] - 1 if row[0] else 0
        logger.debug(f"PostgresOperator.fetch_offset: Offset - {offset}")
        return offset
