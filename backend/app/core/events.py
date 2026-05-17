import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class NewsBroadcaster:
    def __init__(self):
        self.queues = set()

    async def subscribe(self):
        q = asyncio.Queue()
        self.queues.add(q)
        try:
            while True:
                msg = await q.get()
                yield msg
        finally:
            self.queues.remove(q)

    def broadcast(self, message: dict):
        msg_str = f"data: {json.dumps(message)}\n\n"
        for q in self.queues:
            q.put_nowait(msg_str)

news_broadcaster = NewsBroadcaster()
