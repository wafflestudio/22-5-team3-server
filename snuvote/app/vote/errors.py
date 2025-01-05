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


class ParticipationCodeError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_400_BAD_REQUEST, "Participation code is required but not provided")