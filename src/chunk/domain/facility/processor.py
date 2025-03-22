from typing import Protocol


class Processor(Protocol):
    async def handle(self, offset: int, uploaded_files: list) -> bool: ...
