from pydantic import BaseModel


class UserModel(BaseModel):
    username: str
    password: str
    email: str = ""
    first_name: str | None = None
    last_name: str | None = None
