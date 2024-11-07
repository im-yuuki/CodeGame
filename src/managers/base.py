import asyncio
import logging
import fastapi
from fastapi import FastAPI

from api.websocket import WebSocketManager
from managers.contests import Contest
from managers.problems import ProblemManager

logger = logging.getLogger(__name__)


class BaseLoader:
    def __init__(self):
        self.server: FastAPI = fastapi.FastAPI()
        self.__ws_manager__ = WebSocketManager()
        self.server.mount("/ws", self.__ws_manager__)
        self.problem_manager = ProblemManager()
        self.contest: Contest = Contest(self.problem_manager, self.broadcast)
        self.server.add_api_route("/", self.root)
        self.server.add_api_route("/index.html", self.root)
        self.server.add_api_route("/favicon.ico", self.favicon)


    async def root(self):
        return fastapi.responses.RedirectResponse("/ui/index.html")
    
    async def favicon(self):
        return fastapi.responses.RedirectResponse("/ui/favicon.ico")
    
        
    def broadcast(self, message: dict):
        asyncio.create_task(self.__ws_manager__.broadcast(message))
        
        
    def reset_contest(self):
        if self.contest:
            self.contest.stop()
        self.contest = Contest(self.problem_manager, self.broadcast)
        self.broadcast({"event": "CONTEST_RESET"})
        logger.info("Contest has been reset")
        
        