from datetime import datetime
from typing import List
from snuvote.database.models import Vote, Choice, ChoiceParticipation
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

class ChoiceDetailResponse(BaseModel):
    choice_id: int
    choice_content: str
    choice_num_participants: int|None = None
    choice_participants_name: List[str]|None = None
    
    # Choice를 받아 ChoiceDetailResponse로 변환
    @staticmethod
    def from_choice(choice: Choice, annonymous_choice, realtime_result) -> "ChoiceDetailResponse":
        id = choice.id
        content = choice.choice_content
        num_participants = len(choice.choice_participations)
        participants_name = [choice_participation.user.name for choice_participation in choice.choice_participations]

        # 익명 투표인 경우 -> choice_participants_name = None
        if annonymous_choice:
            participants_name = None
        
        # 실시간 결과 공개 투표가 아닌 경우
        if not realtime_result:
            num_participants = None
            participants_name = None
        
        return ChoiceDetailResponse(
            choice_id=id,
            choice_content=content,
            choice_num_participants=num_participants,
            choice_participants_name=participants_name
        )


class VoteDetailResponse(BaseModel):
    writer_name: str
    title: str
    content: str
    realtime_result: bool
    multiple_choice: bool
    annonymous_choice: bool
    create_datetime: datetime
    end_datetime: datetime
    choices: List[ChoiceDetailResponse]

