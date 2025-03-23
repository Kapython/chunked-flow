import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chunk.application.services.feed import FeedService
from src.chunk.infra.processor import Processor
from src.chunk.infra.storage import Saver


@patch("time.time", return_value=1680000000)
@pytest.mark.asyncio
async def test_feed_stops_on_no_data(mocker):
    """Test that `feed()` stops when processor handle returns False."""
    mock_settings = MagicMock()
    mock_settings.chunk_size = 10
    mock_settings.concurrency_limit = 2
    mock_settings.metadata_file_name = "metadata_{timestamp}.json"

    mock_pool = MagicMock()
    mock_processor = AsyncMock(spec=Processor)
    mock_saver = AsyncMock(spec=Saver)

    mock_processor.handle.side_effect = [True, True, False]
    call_count = 3
    mock_time = 1680000000

    feed_service = FeedService(
        settings=mock_settings,
        pool=mock_pool,
        processor=mock_processor,
        metadata=mock_saver,
    )

    await feed_service.feed()

    assert mock_processor.handle.call_count == call_count
    mock_saver.save_data.assert_awaited_once_with(
        data=feed_service.create_metadata_file(mock_time),
        file_name=mock_settings.metadata_file_name.format(timestamp=mock_time),
    )


@pytest.mark.asyncio
async def test_feed_creates_metadata_file(mocker):
    """Test that `create_metadata_file` generates the correct metadata."""
    mock_settings = MagicMock()
    mock_settings.chunk_size = 10
    mock_settings.concurrency_limit = 2
    mock_settings.metadata_file_name = "metadata_{timestamp}.json"

    mock_pool = MagicMock()
    mock_processor = AsyncMock(spec=Processor)
    mock_saver = AsyncMock(spec=Saver)

    feed_service = FeedService(
        settings=mock_settings,
        pool=mock_pool,
        processor=mock_processor,
        metadata=mock_saver,
    )

    mock_time = 1680000000
    mocker.patch("time.time", return_value=mock_time)

    feed_service.uploaded_files = ["file1.json.gz", "file2.json.gz"]

    metadata_str = feed_service.create_metadata_file(mock_time)

    metadata = json.loads(metadata_str)
    assert metadata["generation_timestamp"] == mock_time
    assert metadata["name"] == "reservewithgoogle.entity"
    assert metadata["data_file"] == ["file1.json.gz", "file2.json.gz"]


@pytest.mark.asyncio
async def test_semaphore_wrapper(mocker):
    """Test that `semaphore_wrapper` calls processor handle under semaphore."""
    mock_settings = MagicMock()
    mock_settings.chunk_size = 10
    mock_settings.concurrency_limit = 2

    mock_pool = MagicMock()
    mock_processor = AsyncMock(spec=Processor)
    mock_saver = AsyncMock(spec=Saver)

    feed_service = FeedService(
        settings=mock_settings,
        pool=mock_pool,
        processor=mock_processor,
        metadata=mock_saver,
    )

    mock_processor.handle.return_value = True

    result = await feed_service.semaphore_wrapper(0)

    assert result is True
    mock_processor.handle.assert_awaited_once_with(0, feed_service.uploaded_files)


@patch("time.time", return_value=1680000000)
@pytest.mark.asyncio
async def test_feed_with_multiple_chunks(mocker):
    """Test `feed()` processes multiple chunks with proper concurrency."""
    mock_settings = MagicMock()
    mock_settings.chunk_size = 10
    mock_settings.concurrency_limit = 2
    mock_settings.metadata_file_name = "metadata_{timestamp}.json"

    mock_pool = MagicMock()
    mock_processor = AsyncMock(spec=Processor)
    mock_saver = AsyncMock(spec=Saver)

    mock_processor.handle.side_effect = [True, True, True, False]
    call_count = 4
    mock_time = 1680000000

    feed_service = FeedService(
        settings=mock_settings,
        pool=mock_pool,
        processor=mock_processor,
        metadata=mock_saver,
    )

    await feed_service.feed()

    assert mock_processor.handle.call_count == call_count
    mock_saver.save_data.assert_awaited_with(
        data=feed_service.create_metadata_file(mock_time),
        file_name=mock_settings.metadata_file_name.format(timestamp=mock_time),
    )
