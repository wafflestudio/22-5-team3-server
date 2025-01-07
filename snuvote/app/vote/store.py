from functools import cache
from typing import Annotated, List
from datetime import datetime, timedelta

from fastapi import Depends
from snuvote.database.models import Vote, Choice

from snuvote.database.connection import get_db_session
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

class VoteStore:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session
    

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
        
        create_datetime = datetime.now()


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
        self.session.flush()

        for choice_content_input in choices:
            choice = Choice(vote_id=vote.id,
                            choice_content = choice_content_input)
            self.session.add(choice)
        
        self.session.commit()          

        return vote
    
    # 진행 중인 투표 리스트 조회
    def get_ongoing_list(self) -> List[Vote]:
        return self.session.execute(select(Vote).where(Vote.end_datetime > datetime.now())).scalars().all()

    # 투표글 상세 내용 조회
    def get_vote_by_vote_id(self, vote_id: int) -> Vote:
        return self.session.scalar(select(Vote).where(Vote.id == vote_id))