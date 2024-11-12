import logging
from typing import Optional

import fastapi

from managers.base import BaseLoader
from managers.problems import Problem
from utils import auth
from utils.enums import ContestProgress

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
            if not isinstance(name, str) or len(name) < 3:
                raise ValueError()
        except:
            return fastapi.Response(status_code=400, content="Bad request")
        
        uid = self.base.contest.add_contestant(name)
        token = auth.generate_token(uid)
        return fastapi.responses.JSONResponse(
            status_code=200,
            content={"uid": str(uid), "token": token}
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
    
    
    async def get_content(self, request: fastapi.Request, name: str):
        _auth = self.__authorize__(request)
        if _auth is not None:
            return _auth
        if self.base.contest.progress is not ContestProgress.IN_PROGRESS:
            return fastapi.Response(status_code=400, content="Contest is not in progress")
        target = self.__find_problem__(name)
        if target is None:
            return fastapi.Response(status_code=404, content="Problem not found")
        return target.content
    
    
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
            return fastapi.Response(status_code=200, content="Success")
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
            data = {
                "id": str(uid),
                "name": self.base.contest.contestants[uid].name,
                "contest_progress": self.base.contest.progress.name
            }
            
            if self.base.contest.progress is ContestProgress.IN_PROGRESS:
                data["contest"] = {
                    "remaining": self.base.contest.remaining,
                    "problems": [problem.name for problem in self.base.contest.problems],
                    "supported_languages": ["c", "cpp", "rust"]
                }
            if self.base.contest.progress is not ContestProgress.NOT_STARTED:
                data["score"] = contestant.score
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
            # TODO
            return fastapi.Response(status_code=200, content="Success")
        except Exception as e:
            logger.error(f"Failed to submit: {e}")
            return fastapi.Response(status_code=400, content="Bad request")