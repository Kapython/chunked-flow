from unittest.mock import AsyncMock, MagicMock

import pytest

from src.chunk.infra.processor import ChunkProcessor


@pytest.mark.asyncio
async def test_handle_returns_true_when_data_fetched_and_saved(mocker):
    mock_fetcher = AsyncMock()
    mock_fetcher.fetch_data.return_value = ["row1", "row2"]

    mock_payload = MagicMock()
    mock_payload.build_payload = AsyncMock(return_value="json_data")
    mock_payload.compress = AsyncMock(return_value=b"compressed_data")

    mock_saver = MagicMock()
    mock_saver.save_data = AsyncMock()

    processor = ChunkProcessor(
        settings=mocker.MagicMock(chunk_size=100, db_table_name="facility"),
        pool=mocker.MagicMock(),
        payload=mock_payload,
        storage=mock_fetcher,
        saver=mock_saver,
    )

    uploaded_files = []
    offset = 0
    db_table_name = "facility"

    result = await processor.handle(offset, uploaded_files)

    assert result is True
    mock_fetcher.fetch_data.assert_awaited_once_with(offset, 100, db_table_name)
    mock_payload.build_payload.assert_awaited_once_with(["row1", "row2"])
    mock_payload.compress.assert_awaited_once_with("json_data")
    mock_saver.save_data.assert_awaited()

    assert len(uploaded_files) == 1
    assert uploaded_files[0].startswith("facility_feed_") and uploaded_files[0].endswith(".json.gz")
