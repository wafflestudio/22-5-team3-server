from typing import Annotated

from fastapi import Depends
from snuvote.database.models import User
from snuvote.app.user.store import UserStore
from snuvote.app.user.errors import InvalidUsernameOrPasswordError, NotAccessTokenError, NotRefreshTokenError, InvalidTokenError, ExpiredTokenError, BlockedRefreshTokenError, InvalidPasswordError, NaverApiError, InvalidNaverTokenError

import jwt
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import uuid4
from dotenv import load_dotenv
import os
import bcrypt

import httpx

load_dotenv(dotenv_path = '.env.prod')
SECRET = os.getenv("SECRET_FOR_JWT") # .env.prod에서 불러오기

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class UserService:
    def __init__(self, user_store: Annotated[UserStore, Depends()]) -> None:
        self.user_store = user_store

    
    #회원가입
    def add_user(self, userid: str, password: str, email: str, name: str, college: int) -> User:
        hashed_password = self.hash_password(password)
        return self.user_store.add_user(userid=userid, hashed_password=hashed_password, email=email, name=name, college=college)

    #아이디로 유저 찾기
    def get_user_by_userid(self, userid: str) -> User | None:
        return self.user_store.get_user_by_userid(userid)
    
    #비밀번호 해싱하기
    def hash_password(self, password:str) -> str:
        # 비밀번호를 바이트로 변환
        password_bytes = password.encode('utf-8')
        # 솔트 생성 및 해싱
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        #바이트를 다시 문자열로 변환
        return hashed_password.decode('utf-8')
    
    #비밀번호 검증하기
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        # 저장된 해시를 바이트로 변환
        hashed_password_bytes = hashed_password.encode('utf-8')
        # 입력된 비밀번호와 비교
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_bytes)
    
    #토큰 생성
    def issue_tokens(self, userid: str) -> tuple[str, str]:
        access_payload = {
            "sub": userid, # 추후 성능 개선을 위해 payload에 단과대 등 추가
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "typ": TokenType.ACCESS.value, # "typ": "access"
        }
        access_token = jwt.encode(access_payload, SECRET, algorithm="HS256")

        refresh_payload = {
            "sub": userid,
            "jti": uuid4().hex, # 토큰의 고유 ID 생성 -> BlockedRefreshToken.token_id로 사용
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
            "typ": TokenType.REFRESH.value, # "typ": "refresh"
        }
        refresh_token = jwt.encode(refresh_payload, SECRET, algorithm="HS256")
        return access_token, refresh_token

    #처음 로그인
    def signin(self, userid: str, password: str) -> tuple[str, str]:
        user = self.get_user_by_userid(userid)
        if user is None or not self.verify_password(password, user.hashed_password):
            raise InvalidUsernameOrPasswordError()
        return self.issue_tokens(userid)
    
    #엑세스토큰 검증
    def validate_access_token(self, token: str) -> str:
        """
        access_token을 검증하고, username을 반환합니다.
        """
        try:
            payload = jwt.decode(
                token, SECRET, algorithms=["HS256"], options={"require": ["sub"]}
            )
            if payload["typ"] != TokenType.ACCESS.value: # payload["typ"]  != "access"
                raise NotAccessTokenError()
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()


    #리프레쉬토큰 검증
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
            raise NotRefreshTokenError()
        if self.user_store.is_refresh_token_blocked(payload["jti"]):
            raise BlockedRefreshTokenError()
        
        return payload["sub"]

    #만료된 리프레쉬토큰 블랙하기
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

    #토큰 새로 발급
    def reissue_tokens(self, refresh_token: str) -> tuple[str, str]:
        userid = self.validate_refresh_token(refresh_token)
        self.block_refresh_token(refresh_token)
        return self.issue_tokens(userid)
    

    #비밀번호 변경
    def reset_password(self, user:User, current_password:str, new_password:str) -> None:

        #현재 비밀번호를 틀린 경우
        if not self.verify_password(current_password, user.hashed_password):
            raise InvalidPasswordError()
        
        #새 비밀번호 해싱하기
        hashed_new_password = self.hash_password(new_password)        
        return self.user_store.reset_password(userid=user.userid, new_password=hashed_new_password)
    
    # 네이버 access_token 이용해 User의 네이버 고유 식별 id 가져오기
    async def get_naver_id(self, access_token: str) -> str:

        url = "https://openapi.naver.com/v1/nid/me" # 네이버 프로필 조회 API
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                if response.status_code == 401 and response.json().get("errorCode") == "024": # "024": 네이버 인증 실패 에러 코드 https://developers.naver.com/docs/login/profile/profile.md
                    raise InvalidNaverTokenError()
                else: raise NaverApiError()
            
            data = response.json()
            naver_id = data.get("response", {}).get("id")   # 회원의 네이버 고유 식별 id
            
        if naver_id is None:
            raise NaverApiError()
            
        return naver_id
            
                                                    

    # 네이버 계정과 연동
    async def link_with_naver(self, user:User, access_token: str) -> None:
        naver_id = await self.get_naver_id(access_token) # 네이버 access_token 이용해 User의 네이버 고유 식별 id 가져오기
        self.user_store.link_with_naver(user.userid, naver_id) # User의 네이버 고유 식별 id 등록




