from pydantic import BaseModel
from datetime import datetime, timedelta


class Token(BaseModel):
    token: str
    iat_utc: datetime
    ttl_td: timedelta


class JWTTokenPair(BaseModel):
    access_jwt_token: Token
    refresh_jwt_token: Token

    def render_to_user(self):
        return {"refresh_token": self.refresh_jwt_token.token,
                "access_token": self.access_jwt_token.token}
