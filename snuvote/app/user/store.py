from functools import cache
from typing import Annotated

from fastapi import Depends
from snuvote.app.user.errors import EmailAlreadyExistsError, UserUnsignedError, UserIdAlreadyExistsError
from snuvote.database.models import User

from snuvote.database.connection import get_db_session
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

class UserStore:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session


    def add_user(self, userid: str, password: str, email: str, name: str, college: int) -> User:
        if self.get_user_by_userid(userid):
            raise UserIdAlreadyExistsError()

        if self.get_user_by_email(email):
            raise EmailAlreadyExistsError()

        user = User(userid=userid, password=password, email=email, name=name, college=college)
        self.session.add(user)
        self.session.commit()

        return user


    def get_user_by_userid(self, userid: str) -> User | None:
        return self.session.scalar(select(User).where(User.userid == userid))

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))
