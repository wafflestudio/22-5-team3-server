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

class ChoicesNotProvidedError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_400_BAD_REQUEST, "Choices are not provided")

class ChoiceInvalidFormatError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_400_BAD_REQUEST, "Invalid choice format")

class VoteNotFoundError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_404_NOT_FOUND, "Vote not found")

class MultipleChoicesError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_400_BAD_REQUEST, "Multiple choices not allowed")

class ChoiceNotFoundError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_404_NOT_FOUND, "Choice not found")

class ParticipationCodeNotProvidedError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_403_FORBIDDEN, "Participation code not provided")

class WrongParticipationCodeError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_403_FORBIDDEN, "Wrong participation code")
    
class EndedVoteError(HTTPException):
    def __init__(self) -> None:
        super().__init__(HTTP_403_FORBIDDEN, "Ended vote")