from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from time import time

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time()

    def add_token(self):
        now = time()
        if self.tokens < self.capacity:
            tokens = (now - self.last_refill) * self.refill_rate

            self.tokens = min(self.capacity, self.tokens + tokens)

        self.last_refill = now

    def get_token(self):
        self.add_token()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
    
class RateLimit(BaseHTTPMiddleware):
    def __init__(self, app, bucket: TokenBucket, dispatch = None):
        super().__init__(app, dispatch)
        self.bucket = bucket

    async def dispatch(self, request: Request, call_next):
        if self.bucket.get_token():
                return await call_next(request)
        return Response(status_code=429, content="Rate Limit Execceded")
    
