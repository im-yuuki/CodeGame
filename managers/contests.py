import asyncio
import logging
import random
from typing import Optional
from uuid import UUID

from managers.data import Contestant, Submission
from managers.problems import Problem
from managers.sandbox import SandboxManager
from utils.enums import ContestProgress

logger = logging.getLogger(__name__)


class Contest:
    def __init__(self, get_available_problems: callable, sandbox_manager: SandboxManager, broadcast: callable):
        self.get_available_problems = get_available_problems
        self.sandbox_manager = sandbox_manager
        self.broadcast = broadcast
        self.progress: ContestProgress = ContestProgress.NOT_STARTED
        self.duration: int = 0
        self.elapsed: int = 0
        self.problems: list[Problem] = []
        self.contestants: dict[UUID, Contestant] = {}
        self.supported_languages: list[str] = []
        self._timer: Optional[asyncio.Task] = None
        
        
    async def __timer__(self):
        if self.progress is not ContestProgress.IN_PROGRESS:
            return
        while self.elapsed <= self.duration:
            await asyncio.sleep(1)
            self.elapsed += 1
        self.stop()
        
    
    def add_contestant(self, name: str, color: Optional[str]) -> Optional[UUID]:
        if self.progress is not ContestProgress.NOT_STARTED:
            return None
        c = Contestant(name, color)
        self.contestants[c.id] = c
        self.broadcast({
            "event": "NEW_CONTESTANT",
            "id": str(c.id),
            "name": name,
            "color": color
        })
        logger.info("Added new contestant \"%s\" with id %s", name, c.id)
        return c.id
    
    
    def start(self, duration: int = 1800, problems_qty: int = 3) -> bool:
        if self.progress is not ContestProgress.NOT_STARTED:
            return False
        
        if not self.contestants:
            logger.warning("Starting contest with no contestants")
            return False
        
        self.supported_languages = self.sandbox_manager.get_supported_languages()
        if not self.supported_languages:
            logger.warning("Starting contest with no supported languages")
            return False
        
        available_problems = self.get_available_problems()
        self.problems = random.sample(available_problems, k=min(problems_qty, len(available_problems)))
        if not self.problems:
            logger.warning("Starting contest with no problems")
            return False
        
        self.duration = duration
        self.progress = ContestProgress.IN_PROGRESS
        self._timer = asyncio.create_task(self.__timer__())
        self.broadcast({
            "event": "CONTEST_STARTED",
            "duration": duration,
            "problems": [p.name for p in self.problems],
            "supported_languages": self.supported_languages
        })
        logger.info(f"Contest started. Duration {duration}s. Problems: {len(self.problems)}")
        return True
        
        
    def stop(self) -> bool:
        if self.progress is not ContestProgress.IN_PROGRESS:
            return False
        self.progress = ContestProgress.FINISHED
        for contestant in self.contestants.values():
            contestant.mark_finished()
        if self._timer:
            self._timer.cancel()
            self._timer = None
        if self.elapsed > self.duration:
            logger.info("Contest time's up")
        else:
            logger.info("Contest has been forcefully stopped")
        self.broadcast({
            "event": "CONTEST_STOPPED"
        })
        return True
    
    
    def mark_finished(self, contestant_id: UUID) -> bool:
        if self.progress is not ContestProgress.IN_PROGRESS:
            return False
        if contestant_id not in self.contestants:
            return False
        contestant = self.contestants[contestant_id]
        contestant.mark_finished(self.elapsed)
        contestant.refresh_score()
        self.broadcast({
            "event": "CONTESTANT_FINISHED",
            "id": str(contestant_id),
            "score": self.contestants[contestant_id].refresh_score()
        })
        return True
    
    
    async def submission_callback(self, submission: Submission):
        if self.progress is not ContestProgress.IN_PROGRESS:
            return
        if submission.contestant_id not in self.contestants:
            return
        contestant = self.contestants[submission.contestant_id]
        contestant.add_submission(submission)
        self.broadcast({
            "event": "SUBMISSION_RESULT",
            "id": str(submission.id),
            "contestant": str(contestant.id),
            "problem": submission.problem,
            "language": submission.language,
            "status": submission.status.name,
            "time": submission.time,
            "score": contestant.refresh_score()
        })
        