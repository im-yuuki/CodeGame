import logging

from aiohttp.web_fileresponse import FileResponse
import os

logger = logging.getLogger(__name__)


class Problem:
    def __init__(self, name: str, content: FileResponse):
        self.name: str = name
        self.content: FileResponse = content


def __problem_loader__(name: str) -> Problem:
    path = f"problems/{name}"
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Problem {name} not found")
    open(f"{path}/content.pdf", "rb").close()
    content = FileResponse(f"{path}/content.pdf")
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
        