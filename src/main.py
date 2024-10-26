import fastapi
import uvicorn
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles


class BaseLoader:
    def __init__(self):
        self.server = fastapi.FastAPI()
        self.server.mount("/", StaticFiles(directory="web", html=True))
    
    def run(self, port: int = 8080):
        uvicorn.run(
            self.server,
            host="0.0.0.0",
            port=port,
            loop="asyncio"
        )
        

if __name__ == "__main__":
    load_dotenv()
    PORT: int = int(os.getenv("PORT", 8080))
    
    app = BaseLoader()
    app.run(port=PORT)
