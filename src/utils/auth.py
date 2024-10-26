from typing import Optional
import uuid
import jwt
import os

jwt_secret = os.getenv("JWT_SECRET", "dev")


def generate_token(user_id: uuid.UUID) -> str:
    return jwt.encode({"user_id": str(user_id)}, jwt_secret, algorithm="HS256")


def verify_token(token: str) -> Optional[uuid.UUID]:
    try:
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return uuid.UUID(decoded["user_id"])
    except:
        return None
