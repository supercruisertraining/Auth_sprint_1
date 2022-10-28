from uuid import UUID

from pydantic import BaseModel


class UserRegisterModel(BaseModel):
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class UserUpdateModel(BaseModel):
    username: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserModel(BaseModel):
    id: str | UUID
    username: str
    password: str
    role: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        orm_mode = True
