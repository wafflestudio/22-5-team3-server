from datetime import datetime
from typing import List
from snuvote.database.models import Vote
from pydantic import BaseModel



class VotesListInfoResponse(BaseModel):
    id: int
    title: str
    content: str
    create_datetime: datetime
    end_datetime: datetime

    @staticmethod
    def from_vote(vote: Vote) -> "VotesListInfoResponse":
        return VotesListInfoResponse(
            id=vote.id,
            title=vote.title,
            content=vote.content,
            create_datetime=vote.create_datetime,
            end_datetime=vote.end_datetime
        )

class OnGoingVotesListResponse(BaseModel):
    votes_list: List[VotesListInfoResponse]
    has_next: bool
    next_cursor: str|None = None