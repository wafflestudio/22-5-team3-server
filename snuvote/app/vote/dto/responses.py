from datetime import datetime, timezone, timedelta
from typing import List, Annotated

from snuvote.database.models import Vote, User, Choice, ChoiceParticipation
from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator

KST = timezone(timedelta(hours=9), "KST")

def convert_utc_to_ktc_naive(value: datetime) -> datetime:
    value = value.replace(tzinfo=timezone.utc).astimezone(KST).replace(tzinfo=None) # UTC 시간대 주입 후 KST 시간대로 변환한 뒤 offset-naive로 변환
    return value


class VotesListInfoResponse(BaseModel):
    id: int
    title: str
    content: str
    create_datetime: Annotated[datetime, AfterValidator(convert_utc_to_ktc_naive)] # UTC 시간대를 KST 시간대로 변환한 뒤 offset-naive로 변환
    end_datetime: Annotated[datetime, AfterValidator(convert_utc_to_ktc_naive)] # UTC 시간대를 KST 시간대로 변환한 뒤 offset-naive로 변환
    participated: bool

    @staticmethod
    def from_vote_user(vote: Vote, user: User) -> "VotesListInfoResponse":

        # 해당 유저의 참여 여부도 포함시켜야 함
        participated = False
        for choice in vote.choices:
            for choice_participation in choice.choice_participations:
                if choice_participation.user_id == user.id:
                    participated = True
                    break

        return VotesListInfoResponse(
            id=vote.id,
            title=vote.title,
            content=vote.content,
            create_datetime=vote.create_datetime,
            end_datetime=vote.end_datetime,
            participated = participated
        )

class OnGoingVotesListResponse(BaseModel):
    votes_list: List[VotesListInfoResponse]
    has_next: bool
    next_cursor: str|None = None

class ChoiceDetailResponse(BaseModel):
    choice_id: int
    choice_content: str
    participated: bool
    choice_num_participants: int|None = None
    choice_participants_name: List[str]|None = None
    
    # Choice를 받아 ChoiceDetailResponse로 변환
    @staticmethod
    def from_choice(choice: Choice, user: User, annonymous_choice, realtime_result) -> "ChoiceDetailResponse":
        id = choice.id
        content = choice.choice_content
        num_participants = len(choice.choice_participations)
        participants_name = [choice_participation.user.name for choice_participation in choice.choice_participations]


        #로그인한 유저가 선택지를 선택했는지 여부
        participated = False
        for choice_participation in choice.choice_participations:
            if user.id == choice_participation.user_id:
                participated = True
                break

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
            participated=participated,
            choice_num_participants=num_participants,
            choice_participants_name=participants_name
        )


class VoteDetailResponse(BaseModel):
    vote_id:int
    writer_name: str
    is_writer: bool
    title: str
    content: str
    participation_code_required: bool
    realtime_result: bool
    multiple_choice: bool
    annonymous_choice: bool
    create_datetime: Annotated[datetime, AfterValidator(convert_utc_to_ktc_naive)] # UTC 시간대를 KST 시간대로 변환한 뒤 offset-naive로 변환
    end_datetime: Annotated[datetime, AfterValidator(convert_utc_to_ktc_naive)] # UTC 시간대를 KST 시간대로 변환한 뒤 offset-naive로 변환
    choices: List[ChoiceDetailResponse]

