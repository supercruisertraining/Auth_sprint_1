from uuid import UUID

from pydantic import BaseModel


class UserRegisterModel(BaseModel):
    username: str | None
    password: str | None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class SuperUserCreationModel(BaseModel):
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
    username: str | None
    password: str | None
    email: str | None
    role: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        orm_mode = True


class UserAdminModel(BaseModel):
    id: str | UUID
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        orm_mode = True


class Oauth2UserInfo(BaseModel):
    social_id: str
    social_type: str
    username: str | None = None
    email: str | None = None
