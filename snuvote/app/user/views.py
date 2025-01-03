from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from snuvote.app.user.dto.requests import UserSignupRequest, UserSigninRequest
from snuvote.app.user.dto.responses import MyProfileResponse, UserSigninResponse
from snuvote.database.models import User
from snuvote.app.user.service import UserService

user_router = APIRouter()



# ȸ�� ����
@user_router.post("/signup", status_code=HTTP_201_CREATED)
def signup(
    signup_request: UserSignupRequest, user_service: Annotated[UserService, Depends()]
):
    

    user = user_service.add_user(
        signup_request.userid, signup_request.password, signup_request.email, signup_request.name, signup_request.college
    )

    return {"id":user.userid, "email":user.email}


# signin API
@user_router.post("/signin", status_code=HTTP_200_OK)
async def signin(
    user_service: Annotated[UserService, Depends()],
    signin_request: UserSigninRequest,
):
    access_token, refresh_token = user_service.signin(
        signin_request.userid, signin_request.password
    )
    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)


