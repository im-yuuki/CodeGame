import asyncio
import logging
import random
from typing import Optional
from uuid import uuid4, UUID

from managers.problems import Problem, ProblemManager
from utils.enums import SubmissionStatus, ContestProgress

logger = logging.getLogger(__name__)


class Submission:
    def __init__(self, problem: str):
        self.id = uuid4()
        self.problem: str = problem
        self.status: SubmissionStatus = SubmissionStatus.PENDING
        self.binary: Optional[bytes] = None
        

class Contestant:
    def __init__(self, name: str):
        self.name: str = name
        self.id: UUID = uuid4()
        self.score: int = 0
        self.finished: int = 0
        self.state: dict[str, SubmissionStatus] = {}
        self.submissions: list[Submission] = []
        
    def refresh_score(self) -> int:
        _sum = 0
        for sub in self.submissions:
            if sub.status is SubmissionStatus.ACCEPTED:
                _sum += 2000
            elif sub.status not in (SubmissionStatus.INTERNAL_ERROR, SubmissionStatus.PENDING):
                _sum -= 100
        if self.finished > 0:
            _sum -= self.finished
            if _sum < 0:
                _sum = 0
        self.score = _sum
        return _sum
    
    def add_s
    
    
    
    

class Contest:
    def __init__(self, problem_manager: ProblemManager, broadcast: callable):
        self.problem_manager = problem_manager
        self.broadcast = broadcast
        self.progress: ContestProgress = ContestProgress.NOT_STARTED 
        self.remaining: int = 0
        self.problems: list[Problem] = []
        self.contestants: dict[UUID, Contestant] = {}
        self._timer: Optional[asyncio.Task] = None
        
        
    async def __timer__(self):
        if self.progress is not ContestProgress.IN_PROGRESS:
            return
        while self.remaining > 0:
            await asyncio.sleep(1)
            self.remaining -= 1
            
            if self.remaining == 300:
                logger.info("5 minutes left")
            elif self.remaining == 60:
                logger.info("1 minute left")
            elif self.remaining == 30:
                logger.info("30 seconds left")
            elif self.remaining == 10:
                logger.info("10 seconds left")
            elif self.remaining == 5:
                logger.info("5 seconds left")
                
        self.stop()
        
    
    def add_contestant(self, name: str) -> Optional[UUID]:
        if self.progress is not ContestProgress.NOT_STARTED:
            return None
        c = Contestant(name)
        self.contestants[c.id] = c
        self.broadcast({
            "event": "NEW_CONTESTANT",
            "id": str(c.id),
            "name": name
        })
        logger.info("Added new contestant \"%s\" with id %s", name, c.id)
        return c.id
    
    
    def start(self, duration: int = 1500, problems_qty: int = 3) -> bool:
        if self.progress is not ContestProgress.NOT_STARTED:
            return False
        self.progress = ContestProgress.IN_PROGRESS
        problems_qty = min(problems_qty, len(self.problem_manager.problems))
        self.problems = random.choices(list(self.problem_manager.problems.values()), k=problems_qty)
        self.remaining = duration + 2
        self._timer = asyncio.create_task(self.__timer__())
        self.broadcast({
            "event": "CONTEST_STARTED",
            "duration": duration,
            "remaining": self.remaining,
            "problems": [p.name for p in self.problems],
            "supported_languages": ["c", "cpp", "rust"]
        })
        logger.info(f"Contest started. Duration {duration}s")
        logger.info(f"Problems: {', '.join(p.name for p in self.problems)} ({len(self.problems)})")
        return True
        
        
    def stop(self) -> bool:
        if self.progress is not ContestProgress.IN_PROGRESS:
            return False
        self.progress = ContestProgress.FINISHED
        for contestant in self.contestants.values():
            contestant.finished = True
        if self._timer:
            self._timer.cancel()
            self._timer = None
        if self.remaining <= 0:
            logger.info("Contest time's up")
            self.remaining = 0
        else:
            logger.info("Contest has been forcefully stopped")
        self.broadcast({
            "event": "CONTEST_STOPPED"
        })
        return True
        
        