from functools import cache
from typing import Annotated

from fastapi import Depends
from snuvote.app.user.errors import EmailAlreadyExistsError, UserUnsignedError, UserIdAlreadyExistsError
from snuvote.app.user.models import User

#아직 db 연결 구현 안했습니다.
#from wapang.database.connection import get_db_session
#from sqlalchemy import select, delete
#from sqlalchemy.orm import Session
#from sqlalchemy.ext.asyncio import AsyncSession

class UserStore:
    def __init__(self) -> None:
        self.id_counter = 0
        self.store: dict[int, User] = {}
        self.userid_index: dict[str, int] = {}
        self.email_index: dict[str, int] = {}


    def add_user(self, userid: str, password: str, email: str):
        if self.get_user_by_userid(userid):
            raise UserIdAlreadyExistsError()

        if self.get_user_by_email(email):
            raise EmailAlreadyExistsError()

        self.id_counter += 1
        user = User(
            id=self.id_counter, userid=userid, password=password, email=email
        )
        self.store[user.id] = user
        self.userid_index[user.userid] = user.id
        self.email_index[user.email] = user.id
        return user

    def get_user_by_userid(self, userid: str) -> User | None:
        user_id = self.userid_index.get(userid)
        if not user_id:
            return None
        return self.store[user_id]
    
    def get_user_by_email(self, email: str) -> User | None:
        user_id = self.email_index.get(email)
        if not user_id:
            return None
        return self.store[user_id]