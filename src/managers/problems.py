import logging

import fastapi
import os

logger = logging.getLogger(__name__)


class Problem:
    def __init__(self, name: str, time_limit_s: int = 0, memory_limit_mib: int = 0, difficulty: int = 0):
        self.name: str = name
        self.time_limit_s: int = time_limit_s
        self.memory_limit_mib: int = memory_limit_mib
        self.difficulty: int = difficulty


class ProblemManager:
    def __init__(self, app: fastapi.FastAPI):
        self.problems = {}
        
        # Load problems from disk
        try:
            count = 0
            for entry in os.scandir("problems"):
                if not entry.is_dir():
                    continue
                if entry.name.startswith("."):
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to load problems: {e}")
            