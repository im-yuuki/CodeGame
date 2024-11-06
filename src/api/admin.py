import os
import uuid
from json import JSONDecodeError
from typing import Optional

import fastapi

from managers.base import BaseLoader
from utils import auth

admin_uid = uuid.uuid4()
admin_password = os.getenv("ADMIN_PASSWORD", "admin")


async def login(request: fastapi.Request):
    try:
        data = await request.json()
        password: Optional[str] = data.get("password", None)
    except:
        password = None
    if password is None:
        return fastapi.Response(status_code=400, content="Bad request")
    if password != admin_password:
        return fastapi.Response(status_code=401, content="Wrong password")
    return fastapi.Response(status_code=200, content=auth.generate_token(admin_uid))


def __authorize__(request: fastapi.Request) -> Optional[fastapi.Response]:
    verification = auth.verify_token(request.headers.get("Authorization", None))
    if verification is None or verification != admin_uid:
        return fastapi.Response(status_code=401, content="Unauthorized")
    return None


class AdminRouter(fastapi.APIRouter):
    def __init__(self, base: BaseLoader):
        self.base = base
        super().__init__()
        
        # Register the route
        self.add_api_route("/login", login, methods=["POST"])
        self.add_api_route("/start", self.start_contest, methods=["POST"])
        self.add_api_route("/stop", self.stop_contest, methods=["POST"])
        self.add_api_route("/reset", self.reset_contest, methods=["POST"])
    
    
    async def start_contest(self, request: fastapi.Request):
        _auth = __authorize__(request)
        if _auth is not None:
            return _auth
        try:
            data = await request.json()
            duration = data.get("duration", 1500)
            if self.base.contest.start(duration):
                return fastapi.Response(status_code=200, content="Success")
            return fastapi.Response(status_code=409, content="Contest has already started")
        except JSONDecodeError:
            return fastapi.Response(status_code=400, content="Bad request")
    
    
    async def stop_contest(self, request: fastapi.Request):
        _auth = __authorize__(request)
        if _auth is not None:
            return _auth
        if self.base.contest.stop():
            return fastapi.Response(status_code=200, content="Success")
        return fastapi.Response(status_code=409, content="Contest has not started")
    
    
    async def reset_contest(self, request: fastapi.Request):
        _auth = __authorize__(request)
        if _auth is not None:
            return _auth
        self.base.reset_contest()
        return fastapi.Response(status_code=200, content="Success")
    