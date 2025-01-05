from typing import Self
from pydantic import BaseModel

from snuvote.database.models import User



class UserSigninResponse(BaseModel):
    access_token: str
    refresh_token: str