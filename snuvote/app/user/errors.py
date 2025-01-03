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

class InvalidUsernameOrPasswordError():
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Invalid username or password")

class InvalidTokenError():
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Invalid token")

class ExpiredTokenError():
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Expired token")

class BlockedRefreshTokenError():
    def __init__(self) -> None:
        super().__init__(HTTP_401_UNAUTHORIZED, "Blocked refresh token")