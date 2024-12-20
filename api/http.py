import asyncio
import logging
from typing import Optional

import fastapi
from fastapi.responses import Response

from managers.base import BaseLoader
from managers.data import Submission
from managers.problems import Problem
from utils import auth
from utils.enums import ContestProgress, SubmissionStatus

logger = logging.getLogger(__name__)


class ContestantRouter(fastapi.APIRouter):
    def __init__(self, base: BaseLoader):
        self.base = base
        super().__init__()
        
        # Register the routes
        self.add_api_route("/add", self.add_contestant, methods=["POST"])
        self.add_api_route("/problems", self.get_problems_list, methods=["GET"])
        self.add_api_route("/content/{name:path}.pdf", self.get_content, methods=["GET"])
        self.add_api_route("/submit", self.submit, methods=["POST"])
        self.add_api_route("/restore", self.restore, methods=["GET"])
        self.add_api_route("/finish", self.finish, methods=["POST"])
        
    
    def __authorize__(self, request: fastapi.Request) -> Optional[fastapi.Response]:
        verification = auth.verify_token(request.headers.get("Authorization", None))
        if verification is None or verification not in self.base.contest.contestants:
            return fastapi.Response(status_code=401, content="Unauthorized")
        if not self.base.contest:
            return fastapi.Response(status_code=500, content="Internal server error")
        return None
        
        
    async def add_contestant(self, request: fastapi.Request):
        if self.base.contest.progress is not ContestProgress.NOT_STARTED:
            return fastapi.Response(status_code=400, content="Contest already started")
        try:
            data = await request.json()
            name: Optional[str] = data.get("name", None)
            color: Optional[str] = data.get("color", None)
            if not isinstance(name, str) or len(name) < 3:
                raise ValueError()
        except:
            return fastapi.Response(status_code=400, content="Bad request")
        
        uid = self.base.contest.add_contestant(name, color)
        token = auth.generate_token(uid)
        return fastapi.responses.JSONResponse(
            status_code=200,
            content={
                "uid": str(uid),
                "name": name,
                "token": token,
                "color": color
            }
        )
    
    
    async def get_problems_list(self, request: fastapi.Request):
        _auth = self.__authorize__(request)
        if _auth is not None:
            return _auth
        if self.base.contest.progress is not ContestProgress.IN_PROGRESS:
            return fastapi.Response(status_code=400, content="Contest is not in progress")
        return fastapi.responses.JSONResponse(
            status_code=200,
            content=[entry.name for entry in self.base.contest.problems]
        )
    
    
    def __find_problem__(self, name: str) -> Optional[Problem]:
        for problem in self.base.contest.problems:
            if problem.name == name:
                return problem
        return None
    
    
    async def get_content(self, name: str):
        if self.base.contest.progress is not ContestProgress.IN_PROGRESS:
            return fastapi.Response(status_code=400, content="Contest is not in progress")
        target = self.__find_problem__(name)
        if target is None:
            return fastapi.Response(status_code=404, content="Problem not found")
        return Response(
            content=target.content,
            headers={
                "Content-Type": "application/pdf"
            }
        )
    
    async def submit(self, request: fastapi.Request):
        _auth = self.__authorize__(request)
        if _auth is not None:
            return _auth
        if self.base.contest.progress is not ContestProgress.IN_PROGRESS:
            return fastapi.Response(status_code=400, content="Contest is not in progress")
        try:
            uid = auth.verify_token(request.headers.get("Authorization", None))
            contestant = self.base.contest.contestants[uid]
            data = await request.form()
            problem: str = data.get("problem", None)
            language: str = data.get("language", None)
            code: bytes = await data.get("code", None).read()
            if not isinstance(problem, str) or not isinstance(language, str) or not isinstance(code, bytes):
                raise ValueError("Request does not match the expected format")
            if contestant.state.get(problem, None) is SubmissionStatus.ACCEPTED:
                return fastapi.Response(status_code=400, content="You already solved this problem")
            submission = Submission(
                contestant_id=contestant.id,
                problem=problem,
                language=language,
                time=self.base.contest.elapsed,
                code=code
            )
            asyncio.create_task(self.base.sandbox_manager.submit(submission, self.base.contest.submission_callback))
            return fastapi.responses.JSONResponse(status_code=200, content={
                "id": str(submission.id),
                "problem": submission.problem,
                "language": submission.language,
                "result": submission.status.name,
                "time": submission.time
            })
        except Exception as e:
            logger.error(f"Failed to submit: {e}")
            return fastapi.Response(status_code=400, content="Bad request")
        
        
    async def restore(self, request: fastapi.Request):
        _auth = self.__authorize__(request)
        if _auth is not None:
            return _auth
        try:
            uid = auth.verify_token(request.headers.get("Authorization", None))
            contestant = self.base.contest.contestants[uid]
            progress = self.base.contest.progress
            if contestant.finished > 0 and self.base.contest.progress is ContestProgress.IN_PROGRESS:
                progress = ContestProgress.FINISHED
            data = {
                "uid": str(uid),
                "name": contestant.name,
                "contest_progress": progress.name,
                "contestants": []
            }
            for c in self.base.contest.contestants.values():
                data["contestants"].append({
                    "uid": str(c.id),
                    "name": c.name,
                    "color": c.color,
                    "score": c.score,
                    "progress": {problem: status.name for problem, status in c.state.items()},
                    "finished": c.finished
                })
            if contestant.color is not None:
                data["color"] = contestant.color
            if progress is ContestProgress.IN_PROGRESS:
                data["contest"] = {
                    "duration": self.base.contest.duration,
                    "elapsed": self.base.contest.elapsed,
                    "problems": [problem.name for problem in self.base.contest.problems],
                    "supported_languages": self.base.contest.supported_languages
                }
                data["submissions"] = []
                for submission in contestant.submissions:
                    data["submissions"].append({
                        "id": str(submission.id),
                        "problem": submission.problem,
                        "language": submission.language,
                        "result": submission.status.name,
                        "time": submission.time
                    })
            logger.info(f"Restored session for {contestant.name}")
            return fastapi.responses.JSONResponse(status_code=200, content=data)
        except Exception as e:
            logger.error(f"Failed to restore session: {e}")
            return fastapi.Response(status_code=500, content="Failed to restore session")
    
    
    async def finish(self, request: fastapi.Request):
        _auth = self.__authorize__(request)
        if _auth is not None:
            return _auth
        try:
            uid = auth.verify_token(request.headers.get("Authorization", None))
            if self.base.contest.mark_finished(uid):
                return fastapi.Response(status_code=200, content="Success")
            return fastapi.Response(status_code=400, content="Bad request")
        except Exception as e:
            logger.error(f"Failed to mark finished: {e}")
            return fastapi.Response(status_code=400, content="Bad request")
        