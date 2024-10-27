import fastapi

from managers.base import BaseLoader


class AdminRouter(fastapi.APIRouter):
    def __init__(self, base: BaseLoader):
        self.base = base
        super().__init__(prefix="/api/admin")
        
        # Register the route
        self.add_api_route("/login", self.login, methods=["POST"])
        
    
    async def login(self, request: fastapi.Request):
        pass