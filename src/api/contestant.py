import logging
from typing import Optional

import fastapi

from managers.base import BaseLoader
from managers.problems import Problem
from utils import auth

logger = logging.getLogger(__name__)


class ContestantRouter(fastapi.APIRouter):
    def __init__(self, base: BaseLoader):
        self.base = base
        super().__init__()
        
        # Register the routes
        self.add_api_route("/add", self.add_contestant, methods=["POST"])
        self.add_api_route("/problems", self.get_problems_list, methods=["GET"])
        self.add_api_route("/problem/{name:path}", self.get_problem, methods=["GET"])
        self.add_api_route("/content/{name:path}.pdf", self.get_content, methods=["GET"])
        self.add_api_route("/submit", self.submit, methods=["POST"])
        
    
    def __authorize__(self, request: fastapi.Request) -> Optional[fastapi.Response]:
        verification = auth.verify_token(request.headers.get("Authorization", None))
        if verification is None or verification not in self.base.contest.contestants:
            return fastapi.Response(status_code=401, content="Unauthorized")
        if not self.base.contest:
            return fastapi.Response(status_code=500, content="Internal server error")
        if not self.base.contest.started:
            return fastapi.Response(status_code=409, content="Contest has not started")
        return None
        
        
    async def add_contestant(self, request: fastapi.Request):
        if not self.base.contest:
            return fastapi.Response(status_code=500, content="Internal server error")
        if self.base.contest.started:
            return fastapi.Response(status_code=409, content="Contest has already started")
        try:
            data = await request.json()
            name = data.get("name", None)
            if name is None:
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
        return fastapi.responses.JSONResponse(
            status_code=200,
            content=[entry.name for entry in self.base.contest.problems]
        )
    
    
    def __find_problem__(self, name: str) -> Optional[Problem]:
        for problem in self.base.contest.problems:
            if problem.name == name:
                return problem
        return None
    
    
    async def get_problem(self, request: fastapi.Request, name: str):
        _auth = self.__authorize__(request)
        if _auth is not None:
            return _auth
        target = self.__find_problem__(name)
        if target is None:
            return fastapi.Response(status_code=404, content="Problem not found")
        return fastapi.responses.JSONResponse(
            status_code=200,
            content={
                "name": name,
                "time_limit": target.time_limit_s,
                "memory_limit": target.memory_limit_mib,
            }
        )
    
    async def get_content(self, request: fastapi.Request, name: str):
        _auth = self.__authorize__(request)
        if _auth is not None:
            return _auth
        target = self.__find_problem__(name)
        if target is None:
            return fastapi.Response(status_code=404, content="Problem not found")
        return target.content
    
    
    async def submit(self):
        # TODO
        pass
    