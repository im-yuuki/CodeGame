from fastapi.staticfiles import StaticFiles
from fastapi import Response
import os

import uvicorn
from dotenv import load_dotenv

from api.admin import AdminRouter
from api.contestant import ContestantRouter
from managers.base import BaseLoader
from utils import setup_logging
from utils.ratelimit import TokenBucket, RateLimit
__VERSION__ = '0.0.1'


if __name__ == "__main__":
    # Print the logo
    print("""
__  __            __
\\ \\/ /_  ____  __/ /__(_)
 \\  / / / / / / / //_/ /
 / / /_/ / /_/ / ,< / /
/_/\\__,_/\\__,_/_/|_/_/
      / ___/____  / __/ /__      ______ _________
      \\__ \\/ __ \\/ /_/ __/ | /| / / __ `/ ___/ _ \\
     ___/ / /_/ / __/ /_ | |/ |/ / /_/ / /  /  __/
    /____/\\____/_/  \\__/ |__/|__/\\__/_/_/   \\___/

""")
    setup_logging.setup()
    load_dotenv()
    base = BaseLoader()
    base.server.mount("/ui", StaticFiles(directory="src/web", html=True))
    base.server.mount("/api/admin", AdminRouter(base))
    base.server.mount("/api/contestant", ContestantRouter(base))
    base.server.add_route("/version", Response(content=__VERSION__))
    base.server.add_middleware(RateLimit, bucket=TokenBucket(int(os.getenv("RATELIMIT", 1000)), int(os.getenv("RATELIMIT_RATE", 10))))
    uvicorn.run(
        base.server,
        host="0.0.0.0",
        port=os.getenv("PORT", 8080),
        loop="asyncio",
        log_config=None
    )
    