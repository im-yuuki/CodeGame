import fastapi
import os

import uvicorn
from dotenv import load_dotenv

from managers.base import BaseLoader
from utils import setup_logging


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
    app = fastapi.FastAPI()
    base = BaseLoader(app)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=os.getenv("PORT", 8080),
        loop="asyncio",
        log_config=None
    )
    