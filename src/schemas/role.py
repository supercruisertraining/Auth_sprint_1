from pydantic import BaseModel


class Role(BaseModel):
    role_name: str

    class Config:
        orm_mode = True
