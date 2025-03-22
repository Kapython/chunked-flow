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

    async def fetch_data(self, offset: int, limit: int) -> list[dict]:
        """Fetch a chunk of facility records."""
        rows = await self.get_rows(offset, limit)
        return [dict(row) for row in rows]

    async def get_rows(self, offset: int, limit: int):
        """
        Fetches a paginated list of records from the database.
        """
        start = datetime.now()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, name, phone, url, latitude, longitude, country,
                       locality, region, postal_code, street_address
                FROM facility
                ORDER BY id
                OFFSET $1
                LIMIT $2
                """,
                offset,
                limit,
            )
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
