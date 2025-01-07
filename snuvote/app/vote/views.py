from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

from snuvote.app.vote.dto.requests import CreateVoteRequest
from snuvote.app.vote.dto.responses import OnGoingVotesListResponse, VotesListInfoResponse
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
        writer_id=user.id,
        title=create_vote_request.title,
        content=create_vote_request.content,
        participation_code_required=create_vote_request.participation_code_required,
        participation_code=create_vote_request.participation_code,
        realtime_result=create_vote_request.realtime_result,
        multiple_choice=create_vote_request.multiple_choice,
        annonymous_choice=create_vote_request.annonymous_choice,
        vote_period=create_vote_request.vote_period,
        choices=create_vote_request.choices
    )

    return {"id": vote.id,
            "title":vote.title, 
            "content":vote.content, 
            "choices":vote.choices,
            "participation_code":vote.participation_code, 
            "realtime_result":vote.realtime_result,
            "multiple_choice":vote.multiple_choice, 
            "annonymous_choice":vote.annonymous_choice,
            "create_datetime":vote.create_datetime,
            "end_datetime":vote.end_datetime
            }

# 진행 중인 투표 리스트 조회
@vote_router.get("/ongoing_list", status_code=HTTP_200_OK)
def get_ongoing_list(
    vote_service: Annotated[VoteService, Depends()]
):
    votes = vote_service.get_ongoing_list()
    return OnGoingVotesListResponse(
        votes_list = [ VotesListInfoResponse.from_vote(vote) for vote in votes],
        has_next = True,
        next_cursor = 'next_cursor'
    )