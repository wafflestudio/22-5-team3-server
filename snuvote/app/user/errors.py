from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND
)


class InvalidFieldFormatError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_400_BAD_REQUEST, "Invalid field format")


class MissingRequiredFieldError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_400_BAD_REQUEST, "Missing required fields")




class EmailAlreadyExistsError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_409_CONFLICT, "Email already exists")

class UserIdAlreadyExistsError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_409_CONFLICT, "Username already exists")

class UserUnsignedError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "User is not signed in")

class InvalidUsernameOrPasswordError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Invalid userid or password")

class UserNotFoundError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "User not found")

class NotAccessTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Not an access token")

class NotRefreshTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Not a refresh token")       

class InvalidTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Invalid token")

class ExpiredTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Expired token")

class BlockedRefreshTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Blocked refresh token")

class InvalidPasswordError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Invalid password")

class InvalidConfirmPasswordError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_400_BAD_REQUEST, "Invalid confirm password")

class NaverApiError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Naver API error")

class InvalidNaverTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Invalid Naver token")