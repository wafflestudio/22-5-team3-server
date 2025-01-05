from typing import Annotated

from fastapi import Depends
from snuvote.database.models import Vote
from snuvote.app.vote.store import VoteStore
from snuvote.app.vote.errors import InvalidFieldFormatError, ParticipationCodeError

from datetime import datetime, timedelta



class VoteService:
    def __init__(self, vote_store: Annotated[VoteStore, Depends()]) -> None:
        self.vote_store = vote_store
    
    #투표 추가하기
    def add_vote(self, title: str, 
                 content: str, 
                 participation_code_required: bool, 
                 participation_code: str|None, 
                 realtime_result:bool, 
                 multiple_choice:bool, 
                 annonymous_choice:bool, 
                 vote_period:int,
                 writer_id:int) -> Vote:

        #참여코드가 필요한데 참여코드가 없을 경우 400 에러
        if participation_code_required and not participation_code:
            raise ParticipationCodeError()
        
        return self.vote_store.add_vote(title=title,
                                         content=content, 
                                         participation_code_required=participation_code_required,
                                         participation_code=participation_code, 
                                         realtime_result=realtime_result, 
                                         multiple_choice=multiple_choice, 
                                         annonymous_choice=annonymous_choice, 
                                         vote_period=vote_period,
                                         writer_id=writer_id)
