from typing import Annotated

from fastapi import Depends
from snuvote.database.models import User
from snuvote.app.user.store import UserStore
from snuvote.app.user.errors import InvalidUsernameOrPasswordError, InvalidTokenError, ExpiredTokenError, BlockedRefreshTokenError

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

    def get_user_by_userid(self, userid: str) -> User | None:
        return self.user_store.get_user_by_userid(userid)
    
    def issue_tokens(self, userid: str) -> tuple[str, str]:
        access_payload = {
            "sub": userid, # 추후 성능 개선을 위해 payload에 단과대 등 추가
            "exp": datetime.now() + timedelta(hours=1),
            "typ": TokenType.ACCESS.value, # "typ": "access"
        }
        access_token = jwt.encode(access_payload, SECRET, algorithm="HS256")

        refresh_payload = {
            "sub": userid,
            "jti": uuid4().hex, # 토큰의 고유 ID 생성 -> BlockedRefreshToken.token_id로 사용
            "exp": datetime.now() + timedelta(days=7),
            "typ": TokenType.REFRESH.value, # "typ": "refresh"
        }
        refresh_token = jwt.encode(refresh_payload, SECRET, algorithm="HS256")
        return access_token, refresh_token

    def signin(self, userid: str, password: str) -> tuple[str, str]:
        user = self.get_user_by_userid(userid)
        if user is None or user.password != password:
            raise InvalidUsernameOrPasswordError()
        return self.issue_tokens(userid)
    
    def validate_access_token(self, token: str) -> str:
        """
        access_token을 검증하고, username을 반환합니다.
        """
        try:
            payload = jwt.decode(
                token, SECRET, algorithms=["HS256"], options={"require": ["sub"]}
            )
            if payload["typ"] != TokenType.ACCESS.value: # payload["typ"]  != "access"
                raise InvalidTokenError()
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

    def validate_refresh_token(self, token: str) -> str:
        """
        refresh_token을 검증하고, username을 반환합니다.
        """
        try:
            payload = jwt.decode(
                token,
                SECRET,
                algorithms=["HS256"],
                options={"require": ["sub"]},
            )
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()
        if payload["typ"] != TokenType.REFRESH.value:
            raise InvalidTokenError()
        if self.user_store.is_token_blocked(payload["jti"]):
            raise BlockedRefreshTokenError()
        
        return payload["sub"]

    def block_refresh_token(self, refresh_token: str) -> None:
        """
        refresh_token을 블록합니다.
        """
        payload = jwt.decode(
            refresh_token, SECRET, algorithms=["HS256"], options={"require": ["jti"]}
        )
        token_id = payload["jti"]
        expires_at = datetime.fromtimestamp(payload["exp"])
        self.user_store.block_refresh_token(token_id, expires_at)

    def reissue_tokens(self, refresh_token: str) -> tuple[str, str]:
        userid = self.validate_refresh_token(refresh_token)
        self.block_refresh_token(refresh_token)
        return self.issue_tokens(userid)