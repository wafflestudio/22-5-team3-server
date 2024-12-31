from pydantic import BaseModel


class User(BaseModel):
    id: int
    userid: str
    email: str
    password: str