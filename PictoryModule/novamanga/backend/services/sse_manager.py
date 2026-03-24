import asyncio, json
from typing import AsyncGenerator


class SSEManager:
    def __init__(self):
        self._queues: dict[str, list[asyncio.Queue]] = {}

    def subscribe(self, ref_ids: list[str]) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        for rid in ref_ids:
            self._queues.setdefault(rid, []).append(q)
        return q

    def unsubscribe(self, ref_ids: list[str], q: asyncio.Queue):
        for rid in ref_ids:
            if rid in self._queues:
                try:
                    self._queues[rid].remove(q)
                except ValueError:
                    pass

    def broadcast(self, ref_id: str, data: dict):
        for q in self._queues.get(ref_id, []):
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                pass

    async def stream(self, ref_ids: list[str]) -> AsyncGenerator[str, None]:
        q = self.subscribe(ref_ids)
        try:
            while True:
                data = await asyncio.wait_for(q.get(), timeout=30)
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except asyncio.TimeoutError:
            yield "data: {\"type\":\"heartbeat\"}\n\n"
        finally:
            self.unsubscribe(ref_ids, q)


sse_manager = SSEManager()
