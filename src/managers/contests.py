from uuid import uuid4, UUID


class Contestant:
    def __init__(self, name: str):
        self.name: str = name
        self.id: UUID = uuid4()
        self.state = {}
        self.submission = []


class Contest:
    def __init__(self):
        self.started = False
        self.problems = []
        self.contestants: dict[UUID, Contestant] = {}
    
    def add_contestant(self, name: str) -> UUID:
        c = Contestant(name)
        self.contestants[c.id] = c
        return c.id
    
    
