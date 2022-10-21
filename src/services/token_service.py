from datetime import datetime, timedelta

import jwt

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20


class JWTService:
    def __init__(self, user_id, user_group):
        self.user_id = user_id
        self.user_group = user_group

    def generate_access_token(self):
        payload = {
            "user_id": self.user_id,
            "user_group": self.user_group,
            "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
