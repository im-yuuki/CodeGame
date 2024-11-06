import logging
from typing import Optional

import aiohttp
import asyncio
from uuid import uuid4, UUID

logger = logging.getLogger(__name__)


class Sandbox:
    def __init__(self, url: str):
        self.id = uuid4()
        self.session = aiohttp.ClientSession(base_url=url)
        self.lock = asyncio.Lock()
        self.version: Optional[str] = None
        self.supported_modules: list[str] = []
        self.supported_problems: list[str] = []
        self.ready: bool = False
        self.connect()
        
    async def test_connection(self):
        while True:
            async with self.lock:
                try:
                    async with self.session.get("/version") as resp:
                        self.version = await resp.text()
                    if self.ready:
                        return
                    async with self.session.get("/modules") as resp:
                        data = await resp.json()
                        if not isinstance(data, list):
                            raise ValueError("Response does not match the expected format")
                        self.supported_modules = data
                    async with self.session.get("/problems") as resp:
                        data = await resp.json()
                        if not isinstance(data, list):
                            raise ValueError("Response does not match the expected format")
                        self.supported_problems = data
                    self.ready = True
                except Exception as e:
                    logger.error(f"Sandbox {self.id} disconnected: {e}")
                    self.version = None
                    self.supported_modules = []
                    self.supported_problems = []
                    self.ready = False
                    return
                
            await asyncio.sleep(30)
            
    def connect(self):
        asyncio.create_task(self.test_connection())
        
    async def submit(self, problem: str, code: str):
        async with self.lock:
            pass


class SandboxManager:
    def __init__(self):
        pass

    def add(self):
        pass
    
    def remove(self, node_id: UUID):
        pass