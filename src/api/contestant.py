import fastapi

from managers.base import BaseLoader


class ContestantRouter(fastapi.APIRouter):
    def __init__(self, base: BaseLoader):
        self.base = base
        super().__init__(prefix="/api/users")
        
        # Register the route
        self.add_api_route("/add", self.add_contestant, methods=["POST"])
        
        
        
    async def add_contestant(self, request: fastapi.Request):
        pass