from typing import Annotated

from fastapi import Depends
from snuvote.database.models import User
from snuvote.app.user.store import UserStore
from snuvote.app.user.errors import InvalidUsernameOrPasswordError

import jwt
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4

SECRET = "secret_for_jwt" # .env.prod에서 불러오기

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class UserService:
    def __init__(self, user_store: Annotated[UserStore, Depends()]) -> None:
        self.user_store = user_store

    
    #ȸ������
    def add_user(self, userid: str, password: str, email: str, name: str, college: int):
        return self.user_store.add_user(userid=userid, password=password, email=email, name=name, college=college)
    
    def issue_tokens(self, userid: str) -> tuple[str, str]:
        access_payload = {
            "sub": userid, # 추후 성능 개선을 위해 payload에 단과대 등 추가
            "exp": datetime.now() + timedelta(hours=1),
            "typ": TokenType.ACCESS.value,
        }
        access_token = jwt.encode(access_payload, SECRET, algorithm="HS256")

        refresh_payload = {
            "sub": userid,
            "jti": uuid4().hex,
            "exp": datetime.now() + timedelta(days=7),
            "typ": TokenType.REFRESH.value,
        }
        refresh_token = jwt.encode(refresh_payload, SECRET, algorithm="HS256")
        return access_token, refresh_token

    def signin(self, userid: str, password: str) -> tuple[str, str]:
        user = self.get_user_by_userid(userid)
        if user is None or user.password != password:
            raise InvalidUsernameOrPasswordError()
        return self.issue_tokens(userid)
