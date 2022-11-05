from pydantic import BaseModel


class Role(BaseModel):
    role_name: str
    description: str | None
    position: int

    class Config:
        orm_mode = True
