import logging
from typing import Optional

import aiohttp
import asyncio
from managers.contests import Submission
from uuid import uuid4, UUID

from utils.enums import SubmissionStatus

logger = logging.getLogger(__name__)


class Sandbox:
    def __init__(self, url: str):
        self.id = uuid4()
        self.url = url
        self.session = aiohttp.ClientSession(base_url=url)
        self.lock = asyncio.Lock()
        self.version: Optional[str] = None
        self.supported_modules: list[str] = []
        self.supported_problems: list[str] = []
        self.ready: bool = False
        self.in_queue: int = 0
        asyncio.create_task(self.__connect__())
    
    async def __connect__(self):
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
                    logger.error(f"Lost connection to sandbox {self.id} ({self.url}): {e}")
                    self.version = None
                    self.supported_modules = []
                    self.supported_problems = []
                    self.ready = False
                await asyncio.sleep(30)
            
    
    async def submit(self, submission: Submission):
        self.in_queue += 1
        try:
            async with self.lock:
                pass
        except Exception as e:
            logger.error(f"Failed to submit to sandbox {self.id} ({self.url}): {e}")
        finally:
            self.in_queue -= 1


class SandboxManager:
    def __init__(self):
        self.nodes: dict[UUID, Sandbox] = {}
        try:
            with open("sandboxes.txt", "r") as file:
                for line in file:
                    if not line.startswith("http://") and not line.startswith("https://"):
                        continue
                    self.add(line.strip())
        except Exception as e:
            logger.error(f"Failed to load sandboxes list: {e}")
            
        
    async def __submit__(self, submission: Submission, callback):
        for node in self.nodes.values():
            asyncio.create_task(node.submit(submission))
    
    def add(self, url: str) -> UUID:
        node = Sandbox(url)
        self.nodes[node.id] = node
        logger.info("Added new node %s (%s)", node.id, node.url)
        return node.id
    
    def remove(self, node_id: UUID) -> None:
        result = self.nodes.pop(node_id, None) is not None
        if result:
            logger.info("Removed node %s", node_id)
        return result
    
    
    async def submit(self, submission: Submission, callback):
        list_nodes = []
        for node in self.nodes.values():
            if not node.ready:
                pass
            if submission.problem not in node.supported_problems:
                pass
            if submission.language not in node.supported_modules:
                pass
            list_nodes.append(node)
        if not list_nodes:
            submission.status = SubmissionStatus.INTERNAL_ERROR
            logger.error("No available nodes to process submission %s", submission.id)
        list_nodes.sort(key=lambda x: x.in_queue)
        for node in list_nodes:
            logger.info("Submitting submission %s to node %s", submission.id, node.id)
            await node.submit(submission)
            if submission.status is not SubmissionStatus.INTERNAL_ERROR:
                await callback(submission)
                return
            submission.status = SubmissionStatus.PENDING
        logger.error("Failed to submit submission %s to any node", submission.id)
    
