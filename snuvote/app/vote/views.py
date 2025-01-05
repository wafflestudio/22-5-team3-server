from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

from snuvote.app.vote.dto.requests import CreateVoteRequest
#from snuvote.app.vote.dto.responses import MyProfileResponse, UserSigninResponse
from snuvote.database.models import User
from snuvote.app.vote.service import VoteService
from snuvote.app.vote.errors import InvalidFieldFormatError
from snuvote.app.user.views import login_with_access_token

vote_router = APIRouter()

security = HTTPBearer()

#create vote
@vote_router.post("/create", status_code=HTTP_201_CREATED)
def create_vote(
    user: Annotated[User, Depends(login_with_access_token)],
    create_vote_request: CreateVoteRequest,
    vote_service: Annotated[VoteService, Depends()]
):
    
    vote = vote_service.add_vote(
        create_vote_request.title,
        create_vote_request.content,
        create_vote_request.participation_code_required,
        create_vote_request.participation_code,
        create_vote_request.realtime_result,
        create_vote_request.multiple_choice,
        create_vote_request.annonymous_choice,
        create_vote_request.vote_period,
        user.id
    )

    return {"title":vote.title, 
            "content":vote.content, 
            "participation_code":vote.participation_code, 
            "realtime_result":vote.realtime_result,
            "multiple_choice":vote.multiple_choice, 
            "annonymous_choice":vote.annonymous_choice,
            "create_datetime":vote.create_datetime,
            "end_datetime":vote.end_datetime
            }


