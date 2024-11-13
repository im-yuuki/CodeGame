from fastapi.staticfiles import StaticFiles
import os

import uvicorn
from dotenv import load_dotenv

from api.http import ContestantRouter
from managers.base import BaseLoader
from utils import console


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
    console.setup()
    load_dotenv()
    base = BaseLoader()
    base.server.mount("/ui", StaticFiles(directory="web", html=True))
    base.server.mount("/api", ContestantRouter(base))
    uvicorn.run(
        base.server,
        host="0.0.0.0",
        port=os.getenv("PORT", 8080),
        loop="asyncio",
        log_config=None
    )
    