from functools import cache
from typing import Annotated
from datetime import datetime, timedelta

from fastapi import Depends
from snuvote.app.vote.errors import ParticipationCodeError
from snuvote.database.models import Vote

from snuvote.database.connection import get_db_session
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

class VoteStore:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session
    

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
        
        create_datetime = datetime.now()
        end_datetime = create_datetime + timedelta(days=vote_period)

        #참여코드가 필요한데 참여코드가 없을 경우 400 에러
        if participation_code_required and not participation_code:
            raise ParticipationCodeError()

        vote = Vote(writer_id=writer_id, 
                    create_datetime=create_datetime, 
                    title=title, content=content, 
                    status=True, 
                    end_datetime=end_datetime, 
                    participation_code_required=participation_code_required,
                    participation_code=participation_code,
                    realtime_result=realtime_result,
                    multiple_choice=multiple_choice,
                    annonymous_choice=annonymous_choice
                    )

        self.session.add(vote)
        self.session.commit()

        return vote