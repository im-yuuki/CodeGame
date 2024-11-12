import logging
from datetime import datetime, UTC
from os import makedirs, getpid, kill
from signal import SIGINT
from colorama import Fore, Style, init
from prompt_toolkit.patch_stdout import StdoutProxy
from prompt_toolkit.shortcuts import PromptSession


async def interactive_shell(handler):
    session = PromptSession("[cmd] > ")
    while True:
        try:
            result = await session.prompt_async()
            await handler(result)
        except (EOFError, KeyboardInterrupt):
            return


async def start_shell(handler):
    try:
        await interactive_shell(handler)
    finally:
        kill(getpid(), SIGINT)


def setup() -> None:
    now = int(datetime.now(UTC).timestamp())
    file_name = f"logs/{now}.log"
    # Create log file if not exist
    try:
        open(file_name, "ab").close()
    except FileNotFoundError:
        makedirs("logs", exist_ok=True)
        open(file_name, "wb").close()
    
    # Setup logging
    init(
        autoreset=True
    )
    
    class SpectificLevelFilter(logging.Filter):
        # Logging filter that allow only the spectified level to be processed
        def __init__(self, level: int):
            super().__init__()
            self.level = level
        
        def filter(self, record) -> bool:
            return record.levelno == self.level
    
    # Format (console only)
    INFO_FORMAT = f"{Style.DIM}[%(asctime)s]{Style.RESET_ALL} [%(name)s:%(lineno)d] {Fore.GREEN}[%(levelname)s] - %(message)s{Style.RESET_ALL}"
    WARNING_FORMAT = f"{Style.DIM}[%(asctime)s]{Style.RESET_ALL} [%(name)s:%(lineno)d] {Fore.YELLOW}[%(levelname)s] - %(message)s{Style.RESET_ALL}"
    ERROR_FORMAT = f"{Style.DIM}[%(asctime)s]{Style.RESET_ALL} [%(name)s:%(lineno)d] {Fore.RED}[%(levelname)s] - %(message)s{Style.RESET_ALL}"
    
    DATEFMT = "%d-%m-%Y %H:%M:%S"
    
    # Create handlers
    proxy = StdoutProxy(raw=True)
    info_handler = logging.StreamHandler(proxy)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(SpectificLevelFilter(logging.INFO))
    info_handler.setFormatter(logging.Formatter(INFO_FORMAT, datefmt=DATEFMT))
    
    warning_handler = logging.StreamHandler(proxy)
    warning_handler.setLevel(logging.WARNING)
    warning_handler.addFilter(SpectificLevelFilter(logging.WARNING))
    warning_handler.setFormatter(logging.Formatter(WARNING_FORMAT, datefmt=DATEFMT))
    
    error_handler = logging.StreamHandler(proxy)
    error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(SpectificLevelFilter(logging.ERROR))
    error_handler.setFormatter(logging.Formatter(ERROR_FORMAT, datefmt=DATEFMT))
    
    file_handler = logging.FileHandler(file_name, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s:%(lineno)d [%(levelname)s] - %(message)s", datefmt=DATEFMT))
    
    # Configure
    logging.basicConfig(
        level=logging.INFO,
        handlers=[info_handler, warning_handler, error_handler, file_handler]
    )
