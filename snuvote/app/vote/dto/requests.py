from functools import wraps
import re
from typing import Annotated, Callable, TypeVar, List
from pydantic import BaseModel, EmailStr, Field
from pydantic.functional_validators import AfterValidator

from snuvote.app.vote.errors import InvalidFieldFormatError, ChoicesNotProvidedError, ChoiceInvalidFormatError


def validate_title(value: str) -> str:
    if len(value) < 1 or len(value) > 100:
        raise InvalidFieldFormatError()
    return value


def validate_content(value: str) -> str:
    if len(value) < 1 or len(value) > 200:
        raise InvalidFieldFormatError()
    return value

def validate_participation_code(value: str) -> str:
    if len(value) != 6:
        raise InvalidFieldFormatError()
    return value

def validate_vote_period(value: int) -> int:
    if value < 1 or value > 14:
        raise InvalidFieldFormatError()
    return value

def validate_choices(value: List[str]) -> List[str]:
    if len(value) < 1:
        raise ChoicesNotProvidedError()
    for content in value:
        if len(content) < 1 or len(content) > 200:
            raise ChoiceInvalidFormatError()
    return value

T = TypeVar("T")

def skip_none(validator: Callable[[T], T]) -> Callable[[T | None], T | None]:
    @wraps(validator)
    def wrapper(value: T | None) -> T | None:
        if value is None:
            return value
        return validator(value)

    return wrapper


class CreateVoteRequest(BaseModel):
    '''
    제목 : 1~100자
    내용 : 1~200자
    비번 : 6자
    기간 : 1~14
    '''
    title: Annotated[str, AfterValidator(validate_title)]
    content: Annotated[str, AfterValidator(validate_content)]
    participation_code_required: bool
    participation_code: Annotated[str | None, AfterValidator(skip_none(validate_participation_code))] = None
    realtime_result: bool
    multiple_choice: bool
    annonymous_choice: bool
    vote_period: Annotated[int, AfterValidator(validate_vote_period)]
    choices: Annotated[List[str], AfterValidator(validate_choices)]