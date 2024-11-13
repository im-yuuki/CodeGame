import asyncio
import logging
import random
from typing import Optional
from uuid import uuid4, UUID

from managers.problems import Problem, ProblemManager
from utils.enums import SubmissionStatus, ContestProgress

logger = logging.getLogger(__name__)


class Submission:
    def __init__(self, contestant_id: UUID, problem: str, language: str, time: int, code: bytes):
        self.id: UUID = uuid4()
        self.contestant_id: UUID = contestant_id
        self.problem: str = problem
        self.language: str = language
        self.time: int = time
        self.code: bytes = code
        self.status: SubmissionStatus = SubmissionStatus.PENDING
        

class Contestant:
    def __init__(self, name: str, color: Optional[str] = None):
        self.name: str = name
        self.id: UUID = uuid4()
        self.color: Optional[str] = color
        self.score: int = 0
        self.finished: int = 0
        self.state: dict[str, SubmissionStatus] = {}
        self.submissions: list[Submission] = []
        
    def mark_finished(self, time: Optional[int] = None):
        if time is None:
            time = 0
            for sub in self.submissions:
                if sub.status is SubmissionStatus.ACCEPTED:
                    time = max(time, sub.time)
        self.finished = time
        
    def refresh_score(self) -> int:
        _sum = 0
        for sub in self.submissions:
            if sub.status is SubmissionStatus.ACCEPTED:
                _sum += 2000
            elif sub.status not in (SubmissionStatus.INTERNAL_ERROR, SubmissionStatus.PENDING):
                _sum -= 100
        if self.finished > 0:
            _sum -= self.finished
            # if _sum < 0:
            #     _sum = 0
        self.score = _sum
        return _sum
    
    def add_submission(self, submission: Submission) -> bool:
        if submission.problem not in self.state:
            return False
        if submission.status is SubmissionStatus.PENDING:
            return False
        if self.state[submission.problem] is not SubmissionStatus.ACCEPTED:
            self.state[submission.problem] = submission.status
            self.submissions.append(submission)
            self.refresh_score()
        mark_finish = True
        for key in self.state:
            if self.state[key] is not SubmissionStatus.ACCEPTED:
                mark_finish = False
                break
        if mark_finish:
            self.mark_finished()
    

class Contest:
    def __init__(self, problem_manager: ProblemManager, broadcast: callable):
        self.problem_manager = problem_manager
        self.broadcast = broadcast
        self.progress: ContestProgress = ContestProgress.NOT_STARTED
        self.duration: int = 0
        self.elapsed: int = 0
        self.problems: list[Problem] = []
        self.contestants: dict[UUID, Contestant] = {}
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
        self.duration = duration
        self.progress = ContestProgress.IN_PROGRESS
        problems_qty = min(problems_qty, len(self.problem_manager.problems))
        self.problems = random.sample(list(self.problem_manager.problems.values()), k=problems_qty)
        self._timer = asyncio.create_task(self.__timer__())
        self.broadcast({
            "event": "CONTEST_STARTED",
            "duration": duration,
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
            "contestant": str(contestant.id),
            "problem": submission.problem,
            "status": submission.status.name,
            "score": contestant.score
        })
        