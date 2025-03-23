from typing import Protocol


class Payload(Protocol):
    async def build_payload(self, data: list[dict]) -> str: ...

    async def compress(self, data: str) -> bytes: ...
