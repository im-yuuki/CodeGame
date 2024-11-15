import logging
from typing import Optional

import aiohttp
import asyncio

from managers.data import Submission
from uuid import uuid4, UUID

from utils.enums import SubmissionStatus

logger = logging.getLogger(__name__)


class Sandbox:
    def __init__(self, url: str):
        self.id = uuid4()
        self.url = url
        self.session = aiohttp.ClientSession(base_url=url, timeout=aiohttp.ClientTimeout(total=30))
        self.lock = asyncio.Lock()
        self.version: Optional[str] = None
        self.supported_modules: set[str] = set()
        self.supported_problems: set[str] = set()
        self.ready: bool = False
        self.in_queue: int = 0
        self._task = asyncio.create_task(self.__connect__())
        
    
    def stop(self):
        self._task.cancel()
        asyncio.create_task(self.session.close())
        
    
    async def __connect__(self):
        while True:
            async with self.lock:
                try:
                    async with self.session.get("/version") as resp:
                        self.version = await resp.text()
                        
                    async with self.session.get("/modules") as resp:
                        data = await resp.json()
                        if not isinstance(data, list):
                            raise ValueError("Response does not match the expected format")
                        for item in data:
                            if not isinstance(item, str):
                                raise ValueError("Response does not match the expected format")
                            self.supported_modules.add(item)
                            
                    async with self.session.get("/problems") as resp:
                        data = await resp.json()
                        if not isinstance(data, list):
                            raise ValueError("Response does not match the expected format")
                        for item in data:
                            if not isinstance(item, str):
                                raise ValueError("Response does not match the expected format")
                            self.supported_problems.add(item)
                        
                    if not self.ready:
                        logger.info(f"Connected to sandbox {self.id}({self.url}). Version: {self.version}")
                    self.ready = True
                except Exception as e:
                    self.version = None
                    self.supported_modules.clear()
                    self.supported_problems.clear()
                    if self.ready:
                        logger.error(f"Lost connection to sandbox {self.id}: {e}")
                    self.ready = False
            await asyncio.sleep(30)
            
    
    async def submit(self, submission: Submission):
        self.in_queue += 1
        try:
            async with self.lock:
                if not self.ready:
                    submission.status = SubmissionStatus.INTERNAL_ERROR
                    logger.error("Failed to submit to sandbox %s: not ready", self.id)
                    return
                async with self.session.post("/submit", data={
                    "id": str(submission.id),
                    "problem_id": submission.problem,
                    "target_module": submission.language,
                    "file": submission.code
                }) as resp:
                    if resp.status != 200:
                        submission.status = SubmissionStatus.INTERNAL_ERROR
                        raise ValueError(f"Response {resp.status} from sandbox")
                    
                    data = await resp.json()
                    status = data.get("status", None)
                    message = data.get("message", None)
                    if status == "ACCEPTED":
                        submission.status = SubmissionStatus.ACCEPTED
                    elif status == "WRONG_ANSWER":
                        submission.status = SubmissionStatus.WRONG_ANSWER
                    elif status == "COMPILATION_ERROR":
                        submission.status = SubmissionStatus.COMPILATION_ERROR
                    elif status == "RUNTIME_ERROR":
                        submission.status = SubmissionStatus.RUNTIME_ERROR
                    elif status == "TIME_LIMIT_EXCEEDED":
                        submission.status = SubmissionStatus.TIME_LIMIT_EXCEEDED
                    elif status == "MEMORY_LIMIT_EXCEEDED":
                        submission.status = SubmissionStatus.MEMORY_LIMIT_EXCEEDED
                    elif status == "INTERNAL_ERROR":
                        submission.status = SubmissionStatus.INTERNAL_ERROR
                    else:
                        submission.status = SubmissionStatus.INTERNAL_ERROR
                        raise ValueError(
                            f"Unknown response status: {status}" + (". Message: " + message if message else "")
                        )
                    (logger.info if submission.status == SubmissionStatus.ACCEPTED else logger.warning)(
                        "Submission %s finished. Status: %s" + (". Message: " + message if message else ""),
                        submission.id, submission.status.name
                    )
        except Exception as e:
            logger.error(f"Failed to submit to sandbox {self.id}: {e}")
            submission.status = SubmissionStatus.INTERNAL_ERROR
        finally:
            self.in_queue -= 1


class SandboxManager:
    def __init__(self):
        self.nodes: dict[UUID, Sandbox] = {}
        
    def load(self):
        try:
            with open("sandboxes.txt", "r", encoding="utf-8") as file:
                for line in file:
                    if not line.startswith("http"):
                        continue
                    self.add(line.strip())
        except Exception as e:
            logger.error(f"Failed to load sandboxes list: {e}")
            
    
    def add(self, url: str) -> Optional[UUID]:
        if not url.startswith("http"):
            return None
        node = Sandbox(url)
        self.nodes[node.id] = node
        logger.info("Added new node %s (%s)", node.id, node.url)
        return node.id
    
    
    def remove(self, node_id: UUID) -> bool:
        result = self.nodes.pop(node_id, None)
        if result:
            result.stop()
            logger.info("Removed node %s", node_id)
        return result is not None
    
    
    async def submit(self, submission: Submission, callback: callable):
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
            submission.status = SubmissionStatus.PENDING
            logger.info("Submitting submission %s to node %s", submission.id, node.id)
            await node.submit(submission)
            if submission.status is not SubmissionStatus.INTERNAL_ERROR:
                await callback(submission)
                return
            
        logger.error("Submission %s failed on all node", submission.id)
        await callback(submission)
        
        
    def get_supported_languages(self) -> list[str]:
        result = set()
        for node in self.nodes.values():
            result.update(node.supported_modules)
        return list(result)
    
    
    def get_supported_problems(self) -> list[str]:
        result = set()
        for node in self.nodes.values():
            result.update(node.supported_problems)
        return list(result)
    