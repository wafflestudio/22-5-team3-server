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
    is_naver_user: bool
    is_kakao_user: bool

    @staticmethod
    def from_user(user: User) -> "UserInfoResponse":        
        return UserInfoResponse(
            name = user.name,
            userid = user.userid,
            email = user.email,
            college = user.college,
            is_naver_user = user.naver_user != None,
            is_kakao_user = user.kakao_user != None
        )