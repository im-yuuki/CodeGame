import logging

import fastapi
from fastapi.staticfiles import StaticFiles

from managers.problems import ProblemManager

logger = logging.getLogger(__name__)


class BaseLoader:
    def __init__(self, server: fastapi.FastAPI):
        self.server = server
        self.server.mount("/", StaticFiles(directory="src/web", html=True))
        self.problem_manager = ProblemManager(self.server)
        