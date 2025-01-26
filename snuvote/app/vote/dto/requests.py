from functools import wraps
import re
from typing import Annotated, Callable, TypeVar, List
from pydantic import BaseModel, EmailStr, Field
from pydantic.functional_validators import AfterValidator
from datetime import datetime, timezone, timedelta

from snuvote.app.vote.errors import InvalidFieldFormatError, ChoicesNotProvidedError, ChoiceInvalidFormatError, InvalidEndTimeError, DuplicateChoiceError

KST = timezone(timedelta(hours=9), "KST")

def validate_title(value: str) -> str:
    if len(value) < 1 or len(value) > 100:
        raise InvalidFieldFormatError()
    return value


def validate_content(value: str) -> str:
    if len(value) < 1:
        raise InvalidFieldFormatError()
    return value

def validate_participation_code(value: str) -> str:
    if len(value) != 6:
        raise InvalidFieldFormatError()
    #공백이 있으면 에러
    if any(char.isspace() for char in value):
        raise InvalidFieldFormatError()
    
    return value

"""
def validate_vote_period(value: int) -> int:
    if value < 1 or value > 14:
        raise InvalidFieldFormatError()
    return value
"""

def validate_choices(value: List[str]) -> List[str]:
    if len(value) < 1:
        raise ChoicesNotProvidedError()
    for content in value:
        if len(content) < 1 or len(content) > 200:
            raise ChoiceInvalidFormatError()

    return value

def validate_end_datetime(value: datetime) -> datetime:
    value = value.replace(tzinfo=KST).astimezone(timezone.utc) # offset_naive한 value가 한국 시간대였음을 주입하고 UTC로 변환
    if datetime.now(tz=timezone.utc) >= value: 
        raise InvalidEndTimeError()
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
    내용 : 1~자
    비번 : 6자
    기간 : 현재부터~
    '''
    title: Annotated[str, AfterValidator(validate_title)]
    content: Annotated[str, AfterValidator(validate_content)]
    participation_code_required: bool
    participation_code: Annotated[str | None, AfterValidator(skip_none(validate_participation_code))] = None
    realtime_result: bool
    multiple_choice: bool
    annonymous_choice: bool
    end_datetime: Annotated[datetime, AfterValidator(validate_end_datetime)] # end_datetime은 offset_naive임
    choices: Annotated[List[str], AfterValidator(validate_choices)]

#선택지가 중복되면 안됨
def validate_unique_ids(value):
    if len(value) != len(set(value)):
        raise DuplicateChoiceError()
    return value

class ParticipateVoteRequest(BaseModel):
    participated_choice_ids: Annotated[List[int], AfterValidator(validate_unique_ids)]
    participation_code: str | None = None
   

def validate_comment_content(value: str) -> str:
    if len(value) < 1:
        raise InvalidFieldFormatError()
    return value

class CommentRequest(BaseModel):
    content: Annotated[str, AfterValidator(validate_comment_content)]