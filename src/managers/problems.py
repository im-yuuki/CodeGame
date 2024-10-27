import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

logger = logging.getLogger(__name__)


class Problem:
    def __init__(self, name: str, time_limit_s: int = 0, memory_limit_mib: int = 0, difficulty: int = 0):
        self.name: str = name
        self.time_limit_s: int = time_limit_s
        self.memory_limit_mib: int = memory_limit_mib
        self.difficulty: int = difficulty


class ProblemManager:
    def __init__(self, app: FastAPI):
        self.problems = {}
        self.load_problems(app)
        
        
    def load_problems(self, app: FastAPI):
        """Load problems from the problems directory"""
        
        if not os.path.exists("problems"):
            logger.error("No problems directory found")
            return
        count = 0
        for entry in os.scandir("problems"):
            try:
                if not entry.is_dir():
                    continue
                if entry.name.startswith("."):
                    continue
                f = open(f"{entry.path}/config.cfg", "r")
                time_limit_s = 0
                memory_limit_mib = 0
                difficulty = 0
                while True:
                    line = f.readline().strip()
                    if not line:
                        break
                    k, v = line.strip().split("=", 1)
                    if k == "time_limit_s":
                        time_limit_s = int(v)
                    elif k == "memory_limit_mib":
                        memory_limit_mib = int(v)
                    elif k == "difficulty":
                        difficulty = int(v)
                
                app.mount(f"/contents/problems/{entry.name}",
                          StaticFiles(directory=f"{entry.path}/contents", html=True))
                self.problems[entry.name] = Problem(entry.name, time_limit_s, memory_limit_mib, difficulty)
                count += 1
            
            except Exception as e:
                logger.error(f"Failed to load problems {entry.name}: {e}")
        
        logger.info(f"Loaded {count} problems")
        