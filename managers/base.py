import asyncio
import logging
from uuid import UUID

import fastapi
from fastapi import FastAPI
from os import kill, getpid
from signal import SIGINT

from api.ws import WebSocketManager
from managers.contests import Contest
from managers.problems import ProblemManager, Problem
from managers.sandbox import SandboxManager
from utils import console
from utils.enums import ContestProgress

logger = logging.getLogger(__name__)


async def root():
    return fastapi.responses.RedirectResponse("/ui/index.html")


async def favicon():
    return fastapi.responses.RedirectResponse("/ui/favicon.ico")


class BaseLoader:
    def __init__(self):
        self.server: FastAPI = fastapi.FastAPI(on_startup=[
            lambda: asyncio.create_task(console.start_shell(self.handle_shell_command)),
            lambda: self.sandbox_manager.load()
        ])
        self.ws_manager = WebSocketManager()
        self.problem_manager = ProblemManager()
        self.sandbox_manager = SandboxManager()
        self.contest: Contest = Contest(self.get_available_problems, self.sandbox_manager, self.broadcast)
        
        self.server.add_api_route("/", root)
        self.server.add_api_route("/index.html", root)
        self.server.add_api_route("/favicon.ico", favicon)
        self.server.add_websocket_route("/ws", self.ws_manager.endpoint)
        
        
    def get_available_problems(self) -> list[Problem]:
        local: set[str] = set(self.problem_manager.problems.keys())
        in_nodes: set[str] = set(self.sandbox_manager.get_supported_problems())
        return [self.problem_manager.problems[name] for name in local.intersection(in_nodes)]
    
    
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
            except Exception as e:
                logger.warning("Command: \"start\" - Failed: %s", e)
            
        elif command[0] == "stop":
            logger.warning("Command: \"stop\" - %s", 'Success' if self.contest.stop() else 'Failed')
            
        elif command[0] == "reset":
            self.reset_contest()
            logger.warning("Command: \"reset\" - Success")
            
        elif command[0] == "exit":
            logger.warning("Command: \"exit\" - Exiting")
            kill(getpid(), SIGINT)
            
        elif command[0] == "list":
            text = ""
            for node in self.sandbox_manager.nodes.values():
                text += f"{node.id}"
                if not node.ready:
                    text += " - DISCONNECTED\n"
                    continue
                text += f" - Version: {node.version} - In queue: {node.in_queue}\n"
            logger.warning("Command: \"sandboxes\"\n%s", text)
            
        elif command[0] == "languages":
            logger.warning("Command: \"languages\"\n%s", self.sandbox_manager.get_supported_languages())
            
        elif command[0] == "problems":
            logger.warning("Command: \"problems\"\n%s", [problem.name for problem in self.get_available_problems()])
            
        elif command[0] == "add":
            try:
                result = self.sandbox_manager.add(command[1])
                logger.warning("Command: \"add\" - %s", "Success" if result else "Not found")
            except Exception as e:
                logger.warning("Command: \"add\" - Failed: %s", e)
                
        elif command[0] == "remove":
            try:
                result = self.sandbox_manager.remove(UUID(command[1]))
                logger.warning("Command: \"remove\" - %s", "Success" if result is not None else "Not found")
            except Exception as e:
                logger.warning("Command: \"remove\" - Failed: %s", e)
        
        elif command[0] == "contestants":
            text = ""
            for contestant in self.contest.contestants.values():
                text += f"{str(contestant.id)} - {contestant.name} - {contestant.color}\n"
                if self.contest.progress is not ContestProgress.NOT_STARTED:
                    text += f" └ Score: {contestant.score}"
                    for problem in self.contest.problems:
                        text += f" - {problem.name}: {contestant.state.get(problem.name, 'PENDING')}"
                    if contestant.finished > 0:
                        text += f" - Finished at {contestant.finished // 60}m {contestant.finished % 60}s"
                    text += "\n"
            logger.warning("Command: \"contestants\"\n%s", text)
            
        elif command[0] == "help":
            logger.warning("""Command: \"help\"
            List of available commands:
            
            --- General commands ---
            languages - List all supported languages
            problems - List all available problems
            help - Display this help message
            exit - Exit the program
            
            --- Sandbox manage commands ---
            list - List all sandboxes
            add - Add a new sandbox
            remove <node_id> - Remove a sandbox
            
            --- Contest manage commands ---
            contestants - List all contestants
            start [-d <duration>] [-p <number of problems>] - Start the contest
            stop - Stop the contest
            reset - Reset the contest
            """)
        else:
            logger.warning("Unknown command")
            
        
    def broadcast(self, message: dict):
        asyncio.create_task(self.ws_manager.broadcast(message))
        
        
    def reset_contest(self):
        if self.contest:
            self.contest.stop()
        self.contest = Contest(self.get_available_problems, self.sandbox_manager, self.broadcast)
        self.broadcast({"event": "CONTEST_RESET"})
        logger.info("Contest has been reset")
        
        