import asyncio
import gzip
import io
import json
import logging

from src.chunk.domain.facility.payload import Payload

logger = logging.getLogger(__name__)


class ChunkPayload(Payload):
    async def build_payload(self, records: list[dict]) -> str:
        """Transform list of records."""
        data_payload = {"data": []}
        for rec in records:
            data_payload["data"].append(
                {
                    "entity_id": rec["id"],
                    "name": rec["name"],
                    "telephone": rec["phone"],
                    "url": rec["url"],
                    "location": {
                        "latitude": f"{rec['latitude']:.6f}",
                        "longitude": f"{rec['longitude']:6f}",
                        "address": {
                            "country": rec["country"],
                            "locality": rec["locality"],
                            "region": rec["region"],
                            "postal_code": rec["postal_code"],
                            "street_address": rec["street_address"],
                        },
                    },
                }
            )
        logger.debug(f"ChunkPayload.build_payload: Payload size: {len(data_payload)}")
        return json.dumps(data_payload, ensure_ascii=False)

    async def compress(self, data_str: str) -> bytes:
        """Return GZIP-compressed bytes of the data string."""
        buffer = io.BytesIO()
        loop = asyncio.get_running_loop()
        # Run the blocking function in a ThreadPoolExecutor to avoid blocking event loop
        await loop.run_in_executor(
            None,  # use default thread pool
            self._payload_gzip,
            data_str,
            buffer,
        )
        return buffer.getvalue()

    @staticmethod
    def _payload_gzip(data_str: str, buffer: io.BytesIO) -> None:
        """Write GZIP-compressed bytes of the data string to the buffer."""
        with gzip.GzipFile(fileobj=buffer, mode="wb") as gz:
            gz.write(data_str.encode("utf-8"))
