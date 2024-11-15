from typing import Optional
from uuid import UUID, uuid4

from utils.enums import SubmissionStatus


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
        if self.finished > 0:
            return
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
        self.score = _sum
        return _sum
    
    def add_submission(self, submission: Submission) -> bool:
        if submission.problem not in self.state.keys():
            return False
        if submission.status is SubmissionStatus.PENDING:
            return False
        if self.state[submission.problem] is not SubmissionStatus.ACCEPTED:
            self.state[submission.problem] = submission.status
            self.submissions.append(submission)
        mark_finish = True
        for key in self.state:
            if self.state[key] is not SubmissionStatus.ACCEPTED:
                mark_finish = False
                break
        if mark_finish:
            self.mark_finished()
        return True
