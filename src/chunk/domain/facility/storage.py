from typing import Protocol


class Fetcher(Protocol):
    async def fetch_data(self, offset: int, limit: int, table: str) -> list[dict]: ...


class Saver(Protocol):
    async def save_data(self, data: bytes | str, file_name: str) -> bool: ...
