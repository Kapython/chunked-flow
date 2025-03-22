import gzip
import json
from io import BytesIO

import pytest

from src.chunk.infra.payload import ChunkPayload


@pytest.mark.asyncio
async def test_build_payload():
    payload_builder = ChunkPayload()
    records = [
        {
            "id": "facility-1",
            "name": "Facility A",
            "phone": "123456789",
            "url": "https://example.com",
            "latitude": 40.712895,
            "longitude": -74.006070,
            "country": "USA",
            "locality": "New York",
            "region": "NY",
            "postal_code": "10001",
            "street_address": "123 Main Street",
        }
    ]

    data_str = await payload_builder.build_payload(records)
    data = json.loads(data_str)

    assert isinstance(data, dict)
    assert "data" in data
    assert len(data["data"]) == 1

    record = data["data"][0]
    assert record["entity_id"] == "facility-1"
    assert record["name"] == "Facility A"
    assert record["telephone"] == "123456789"
    assert record["location"]["latitude"] == "40.712895"
    assert record["location"]["longitude"] == "-74.006070"
    assert record["location"]["address"]["country"] == "USA"
    assert record["location"]["address"]["locality"] == "New York"
    assert record["location"]["address"]["region"] == "NY"
    assert record["location"]["address"]["postal_code"] == "10001"
    assert record["location"]["address"]["street_address"] == "123 Main Street"


@pytest.mark.asyncio
async def test_compress():
    payload_builder = ChunkPayload()
    data_str = '{"key": "value"}'

    compressed_data = await payload_builder.compress(data_str)

    assert isinstance(compressed_data, bytes), "Compressed data should be bytes."

    with gzip.GzipFile(fileobj=BytesIO(compressed_data), mode="rb") as gz:
        decompressed_data = gz.read().decode("utf-8")
    assert decompressed_data == data_str
