import asyncio
import logging
import fastapi
from fastapi import FastAPI
from os import kill, getpid
from signal import SIGINT

from api.ws import WebSocketManager
from managers.contests import Contest
from managers.problems import ProblemManager
from utils import console

logger = logging.getLogger(__name__)


async def root():
    return fastapi.responses.RedirectResponse("/ui/index.html")


async def favicon():
    return fastapi.responses.RedirectResponse("/ui/favicon.ico")


class BaseLoader:
    def __init__(self):
        self.server: FastAPI = fastapi.FastAPI(on_startup=[lambda: asyncio.create_task(
            console.start_shell(self.handle_shell_command)
        )])
        self.__ws_manager__ = WebSocketManager()
        self.problem_manager = ProblemManager()
        self.contest: Contest = Contest(self.problem_manager, self.broadcast)
        self.server.add_api_route("/", root)
        self.server.add_api_route("/index.html", root)
        self.server.add_api_route("/favicon.ico", favicon)
        self.server.add_websocket_route("/ws", self.__ws_manager__.endpoint)
    
    async def handle_shell_command(self, command_str: str):
        command_str = command_str.strip().lower()
        command = command_str.split(" ")
        if not command:
            return
        if command[0] == "start":
            try:
                duration = 1800
                num_problems = 3
                for i in range(1, len(command)):
                    if command[i] == "-d":
                        duration = int(command[i + 1])
                    elif command[i] == "-p":
                        num_problems = int(command[i + 1])
                logger.warning("Command: \"start\" - %s", 'Success' if self.contest.start(duration, num_problems) else 'Failed')
            except IndexError:
                logger.warning("Command: \"start\" - Invalid format")
                return
        elif command[0] == "stop":
            logger.warning("Command: \"stop\" - %s", 'Success' if self.contest.stop() else 'Failed')
        elif command[0] == "reset":
            self.reset_contest()
            logger.warning("Command: \"reset\" - Success")
        elif command[0] == "exit":
            logger.warning("Command: \"exit\" - Exiting")
            kill(getpid(), SIGINT)
        elif command[0] == "help":
            logger.warning("""Command: \"help\"
            List of available commands:
            start [-d <duration>] [-p <number of problems>] - Start the contest
            stop - Stop the contest
            reset - Reset the contest
            exit - Exit the program
            """)
        else:
            logger.warning("Unknown command")
            
        
    def broadcast(self, message: dict):
        asyncio.create_task(self.__ws_manager__.broadcast(message))
        
        
    def reset_contest(self):
        if self.contest:
            self.contest.stop()
        self.contest = Contest(self.problem_manager, self.broadcast)
        self.broadcast({"event": "CONTEST_RESET"})
        logger.info("Contest has been reset")
        
        