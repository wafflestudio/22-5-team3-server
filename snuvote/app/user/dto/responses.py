from typing import Self
from pydantic import BaseModel

from snuvote.database.models import User



class UserSigninResponse(BaseModel):
    access_token: str
    refresh_token: str

class UserInfoResponse(BaseModel):
    name: str
    userid: str
    email: str
    college: int

    @staticmethod
    def from_user(user: User) -> "UserInfoResponse":
        return UserInfoResponse(
            name = user.name,
            userid = user.userid,
            email = user.email,
            college = user.college
        )