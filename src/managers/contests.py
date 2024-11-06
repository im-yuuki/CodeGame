import asyncio
import logging
import random
from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime, UTC

from managers.problems import Problem, ProblemManager
from utils.enums import SubmissionStatus

logger = logging.getLogger(__name__)


class Submission:
    def __init__(self, problem: str):
        self.problem: str = problem
        self.status: SubmissionStatus = SubmissionStatus.PENDING


class Contestant:
    def __init__(self, name: str):
        self.name: str = name
        self.id: UUID = uuid4()
        self.finished: bool = False
        self.state: dict[str, SubmissionStatus] = {}
        self.submission = []


class Contest:
    def __init__(self, problem_manager: ProblemManager, broadcast: callable):
        self.problem_manager = problem_manager
        self.broadcast = broadcast
        self.started = False
        self.end: int = 0
        self.problems: list[Problem] = []
        self.contestants: dict[UUID, Contestant] = {}
        self._timer: Optional[asyncio.Task] = None
        
        
    async def __timer__(self):
        if not self.started:
            return
        time = self.end - datetime.now(UTC).timestamp()
        if time > 0:
            await asyncio.sleep(time)
        self.stop()
        
    
    def add_contestant(self, name: str) -> UUID:
        c = Contestant(name)
        self.contestants[c.id] = c
        self.broadcast({
            "event": "NEW_CONTESTANT",
            "id": str(c.id),
            "name": name
        })
        logger.info(f"Added new contestant \"{name}\" with id {c.id}")
        return c.id
    
    
    def start(self, duration: int = 1500, problems_qty: int = 3) -> bool:
        if self.started:
            return False
        self.started = True
        if len(self.problem_manager.problems) < problems_qty:
            problems_qty = len(self.problem_manager.problems)
        self.problems = random.choices(list(self.problem_manager.problems.values()), k=problems_qty)
        self.end = datetime.now(UTC).timestamp() + duration
        self._timer = asyncio.create_task(self.__timer__())
        self.broadcast({
            "event": "CONTEST_STARTED",
            "duration": duration,
            "end_time": self.end
        })
        logger.info(f"Contest started. Duration {duration}s")
        logger.info(f"Problems: {', '.join(p.name for p in self.problems)} ({len(self.problems)})")
        return True
        
        
    def stop(self) -> bool:
        if not self.started:
            return False
        for contestant in self.contestants.values():
            contestant.finished = True
        if self._timer:
            self._timer.cancel()
            self._timer = None
            logger.info("Contest time's up")
        else:
            logger.info("Contest has been forcefully stopped")
        self.broadcast({
            "event": "CONTEST_STOPPED"
        })
        return True
        
        