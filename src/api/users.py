import fastapi


class UsersRouter(fastapi.APIRouter):
    def __init__(self):
        super().__init__(prefix="/api/users")
        self.add_api_route("/register", self.register, methods=["POST"])
        
        
    def register(self, request: fastapi.Request):
        pass