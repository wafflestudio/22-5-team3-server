from functools import wraps
import re
from typing import Annotated, Callable, TypeVar, List
from pydantic import BaseModel, EmailStr, Field
from pydantic.functional_validators import AfterValidator

from snuvote.app.user.errors import InvalidFieldFormatError



USERID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")

def validate_userid(value: str) -> str:
    if not re.match(USERID_PATTERN, value):
        raise InvalidFieldFormatError()
    return value


def validate_password(value: str) -> str:
    if len(value) < 8 or len(value) > 20:
        raise InvalidFieldFormatError()

    contains_uppercase = False
    contains_lowercase = False
    contains_digit = False
    contains_special = False

    for char in value:
        #공백있으면 에러
        if char.isspace():
            raise InvalidFieldFormatError()

        if char.isupper():
            contains_uppercase = True
        elif char.islower():
            contains_lowercase = True
        elif char.isdigit():
            contains_digit = True
        else:
            contains_special = True

    constraints_cardinality = sum(
        [contains_uppercase, contains_lowercase, contains_digit, contains_special]
    )
    if constraints_cardinality < 2:
        raise InvalidFieldFormatError()

    return value

class UserSignupRequest(BaseModel):
    userid: Annotated[str, AfterValidator(validate_userid)]
    email: EmailStr
    password: Annotated[str, AfterValidator(validate_password)]
    name: str
    college: int

class UserSigninRequest(BaseModel):
    userid: str
    password: str

class ResetPasswordRequest(BaseModel):
    current_password: str
    new_password: Annotated[str, AfterValidator(validate_password)]