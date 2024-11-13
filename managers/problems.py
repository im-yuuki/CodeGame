import logging
import os

logger = logging.getLogger(__name__)


class Problem:
    def __init__(self, name: str, content: bytes):
        self.name: str = name
        self.content: bytes = content


def __problem_loader__(name: str) -> Problem:
    path = f"problems/{name}"
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Problem {name} not found")
    file = open(f"problems/{name}/content.pdf", "rb")
    content: bytes = file.read()
    return Problem(name, content)


class ProblemManager:
    def __init__(self):
        self.problems: dict[str, Problem] = {}
        
        if not os.path.exists("problems"):
            os.mkdir("problems")
        count = 0
        for entry in os.scandir("problems"):
            try:
                if not entry.is_dir():
                    continue
                if entry.name.startswith("."):
                    continue
                problem = __problem_loader__(entry.name)
                self.problems[entry.name] = problem
                count += 1
            except Exception as e:
                logger.error(f"Failed to load problems {entry.name}: {e}")
        logger.info(f"Loaded {count} problems")
        