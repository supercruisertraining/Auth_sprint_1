from uuid import UUID

from pydantic import BaseModel


class UserRegisterModel(BaseModel):
    username: str
    password: str
    email: str = ""
    first_name: str | None = None
    last_name: str | None = None


class UserModel(BaseModel):
    id: str | UUID
    username: str
    password: str
    role: str | None = None
    email: str = ""
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        orm_mode = True
