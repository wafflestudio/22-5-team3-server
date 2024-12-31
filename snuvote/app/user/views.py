from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from snuvote.app.user.dto.requests import UserSignupRequest
from snuvote.app.user.dto.responses import MyProfileResponse
from snuvote.app.user.models import User
from snuvote.app.user.service import UserService

user_router = APIRouter()



# 회원 가입
@user_router.post("/signup", status_code=HTTP_201_CREATED)
def signup(
    signup_request: UserSignupRequest, user_service: Annotated[UserService, Depends()]
):
    

    user = user_service.add_user(
        signup_request.userid, signup_request.password, signup_request.email
    )

    return {"id":user.userid, "email":user.email}




