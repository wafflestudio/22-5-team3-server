from typing import Annotated, List

from fastapi import Depends
from snuvote.database.models import Vote
from snuvote.app.vote.store import VoteStore
from snuvote.app.vote.errors import InvalidFieldFormatError, ParticipationCodeError

from datetime import datetime, timedelta



class VoteService:
    def __init__(self, vote_store: Annotated[VoteStore, Depends()]) -> None:
        self.vote_store = vote_store
    
    #투표 추가하기
    def add_vote(self,
                 writer_id:int,
                 title: str, 
                 content: str, 
                 participation_code_required: bool, 
                 participation_code: str|None, 
                 realtime_result:bool, 
                 multiple_choice:bool, 
                 annonymous_choice:bool, 
                 end_datetime:datetime,
                 choices: List[str]) -> Vote:

        #참여코드가 필요한데 참여코드가 없을 경우 400 에러
        if participation_code_required and not participation_code:
            raise ParticipationCodeError()
        
        return self.vote_store.add_vote(writer_id=writer_id,
                                        title=title,
                                        content=content, 
                                        participation_code_required=participation_code_required,
                                        participation_code=participation_code, 
                                        realtime_result=realtime_result, 
                                        multiple_choice=multiple_choice, 
                                        annonymous_choice=annonymous_choice, 
                                        end_datetime=end_datetime,
                                        choices=choices)

    # 진행 중인 투표 리스트 조회
    def get_ongoing_list(self) -> List[Vote]:
        return self.vote_store.get_ongoing_list()
    
    # 투표글 상세 내용 조회
    def get_vote_by_vote_id(self, vote_id: int) -> Vote:
        return self.vote_store.get_vote_by_vote_id(vote_id=vote_id)