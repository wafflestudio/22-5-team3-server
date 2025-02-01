from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from snuvote.app.user.dto.requests import UserSignupRequest, UserSigninRequest, ResetPasswordRequest
from snuvote.app.user.dto.responses import UserSigninResponse, UserInfoResponse
from snuvote.database.models import User
from snuvote.app.user.service import UserService
from snuvote.app.user.errors import InvalidTokenError, UserNotFoundError

import secrets
import os
import httpx

user_router = APIRouter()

security = HTTPBearer()

async def login_with_access_token(
    user_service: Annotated[UserService, Depends()],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    token = credentials.credentials # Authorization 헤더에서 Bearer: 를 제외한 token만 추출
    userid = user_service.validate_access_token(token)
    user = await user_service.get_user_by_userid(userid)
    if not user or user.is_deleted:
        raise UserNotFoundError()
    return user



# signup API
@user_router.post("/signup", status_code=HTTP_201_CREATED)
async def signup(
    signup_request: UserSignupRequest, user_service: Annotated[UserService, Depends()]
):
    user = await user_service.add_user(
        signup_request.userid, signup_request.password, signup_request.email, signup_request.name, signup_request.college
    )

    return {"id":user.userid, "email":user.email}


# signin API
@user_router.post("/signin", status_code=HTTP_200_OK)
async def signin(
    user_service: Annotated[UserService, Depends()],
    signin_request: UserSigninRequest,
):
    access_token, refresh_token = await user_service.signin(
        signin_request.userid, signin_request.password
    )
    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)


# refresh API
@user_router.get("/refresh", status_code=HTTP_200_OK)
async def refresh(
    user_service: Annotated[UserService, Depends()],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    refresh_token = credentials.credentials
    access_token, refresh_token = await user_service.reissue_tokens(refresh_token)
    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)

# get_me
@user_router.get("/me", status_code=HTTP_200_OK)
async def get_me(
    user: Annotated[User, Depends(login_with_access_token)]
):
    return UserInfoResponse.from_user(user)

# 회원 탈퇴
@user_router.delete("/me", status_code=HTTP_200_OK)
async def delete_me(
    user: Annotated[User, Depends(login_with_access_token)],
    user_service: Annotated[UserService, Depends()]
):
    await user_service.delete_user(user)
    return "Success"

#비밀번호 변경하기
@user_router.patch("/reset_pw", status_code=HTTP_200_OK)
async def reset_password(
    user: Annotated[User, Depends(login_with_access_token)],
    reset_password_request: ResetPasswordRequest,
    user_service: Annotated[UserService, Depends()]
):
    
    await user_service.reset_password(
        user, reset_password_request.current_password, reset_password_request.new_password
    )

    return "Success"


# 네이버 계정과 연동
@user_router.post("/link/naver", status_code=HTTP_201_CREATED)
async def link_with_naver(
    user: Annotated[User, Depends(login_with_access_token)],
    user_service: Annotated[UserService, Depends()],
    access_token: Annotated[str, Body(...)]  
):
    await user_service.link_with_naver(user, access_token)

    return "Success"

# 네이버 계정으로 로그인
@user_router.post("/signin/naver", status_code=HTTP_200_OK)
async def signin_with_naver_access_token(
    user_service: Annotated[UserService, Depends()],
    naver_access_token: Annotated[str, Body(...)]  
):
    access_token, refresh_token = await user_service.signin_with_naver_access_token(naver_access_token)

    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)

# 카카오 계정과 연동
@user_router.post("/link/kakao", status_code=HTTP_201_CREATED)
async def link_with_kakao(
    user: Annotated[User, Depends(login_with_access_token)],
    user_service: Annotated[UserService, Depends()],
    kakao_access_token: Annotated[str, Body(...)]  
):
    await user_service.link_with_kakao(user, kakao_access_token)
    return "Success"

# 카카오 계정으로 로그인
@user_router.post("/signin/kakao", status_code=HTTP_200_OK)
async def signin_with_kakao_access_token(
    user_service: Annotated[UserService, Depends()],
    kakao_access_token: Annotated[str, Body(...)]  
):
    access_token, refresh_token = await user_service.signin_with_kakao_access_token(kakao_access_token)

    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)