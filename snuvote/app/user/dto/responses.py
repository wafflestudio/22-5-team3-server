from typing import Self
from pydantic import BaseModel

from snuvote.app.user.models import User


class MyProfileResponse(BaseModel):
    username: str
    email: str
    address: str | None
    phone_number: str | None

    @staticmethod
    def from_user(user: User) -> "MyProfileResponse":
        return MyProfileResponse(
            userid=user.userid,
            email=user.email,
        )