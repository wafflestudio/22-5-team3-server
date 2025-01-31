from functools import cache
from typing import Annotated
from datetime import datetime

from fastapi import Depends
from snuvote.app.user.errors import EmailAlreadyExistsError, UserIdAlreadyExistsError, UserNotFoundError, NotLinkedNaverAccountError, NaverLinkAlreadyExistsError, NotLinkedKakaoAccountError, KakaoLinkAlreadyExistsError
from snuvote.database.models import User, BlockedRefreshToken, NaverUser, KakaoUser

from snuvote.database.connection import get_db_session
from sqlalchemy import select, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

class UserStore:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    #회원가입하기
    async def add_user(self, userid: str, hashed_password: str, email: str, name: str, college: int) -> User:
        if await self.get_user_by_userid(userid):
            raise UserIdAlreadyExistsError()

        if await self.get_user_by_email(email):
            raise EmailAlreadyExistsError()

        user = User(userid=userid, hashed_password=hashed_password, email=email, name=name, college=college)
        self.session.add(user)
        await self.session.flush()

        return user

    #아이디로 유저찾기
    async def get_user_by_userid(self, userid: str) -> User | None:
        return await self.session.scalar(select(User).options(joinedload(User.naver_user), joinedload(User.kakao_user)).where(User.userid == userid))

    #이메일로 유저찾기
    async def get_user_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    #만료된 리프레쉬토큰 블랙하기
    async def block_refresh_token(self, token_id: str, expires_at: datetime) -> None:
        blocked_refresh_token = BlockedRefreshToken(token_id=token_id, expires_at=expires_at)
        self.session.add(blocked_refresh_token)
        await self.session.flush()

    #리프레쉬토큰 만료 체크하기
    async def is_refresh_token_blocked(self, token_id: int) -> bool:
        return (
            await self.session.scalar(
                select(BlockedRefreshToken).where(BlockedRefreshToken.token_id == token_id)
            )
            is not None
        )
    
    #비밀번호 변경하기
    async def reset_password(self, userid:str, new_password:str) -> None:
        user = await self.get_user_by_userid(userid)
        user.hashed_password = new_password
        await self.session.flush()

    # 네이버 고유 식별 id 등록
    async def link_with_naver(self, userid: str, naver_id: str):
        user = await self.get_user_by_userid(userid)
        new_naveruser = NaverUser(user_id=user.id, naver_id=naver_id)
        self.session.add(new_naveruser)
        try:
            await self.session.flush()
        except IntegrityError as e:
            if "Duplicate entry" in str(e.orig):
                raise NaverLinkAlreadyExistsError()
            else:
                raise e

    # 네이버 고유 식별 id로 유저 찾기
    def get_user_by_naver_id(self, naver_id: str) -> User:
        user_id = self.session.scalar(select(NaverUser.user_id).where(NaverUser.naver_id == naver_id))
        if user_id is None:
            raise NotLinkedNaverAccountError()

        user = self.session.scalar(select(User).where(User.id == user_id))
        if not user:
            raise UserNotFoundError()
        
        return user

    # 카카오 고유 식별 id 등록
    async def link_with_kakao(self, userid: str, kakao_id: int):
        user = await self.get_user_by_userid(userid)
        new_kakaouser = KakaoUser(user_id=user.id, kakao_id=kakao_id)
        await self.session.add(new_kakaouser)
        try:
            await self.session.flush()
        except IntegrityError as e:
            if "Duplicate entry" in str(e.orig):
                raise KakaoLinkAlreadyExistsError()
            else:
                raise e

    # 카카오 고유 식별 id로 유저 찾기
    def get_user_by_kakao_id(self, kakao_id: int) -> User:
        user_id = self.session.scalar(select(KakaoUser.user_id).where(KakaoUser.kakao_id == kakao_id))
        if user_id is None:
            raise NotLinkedKakaoAccountError()

        user = self.session.scalar(select(User).where(User.id == user_id))
        if not user:
            raise UserNotFoundError()
        
        return user
    
    # 탈퇴하기
    async def delete_user(self, user: User) -> None:
        user.is_deleted = True
        user.name = "탈퇴한 회원"
        await self.session.flush()