from functools import cache
from typing import Annotated, List
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from snuvote.database.models import Vote, Choice, ChoiceParticipation, Comment

from snuvote.database.connection import get_db_session
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

KST = timezone(timedelta(hours=9), "KST")

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
        
        create_datetime = datetime.now(tz=timezone.utc)


        vote = Vote(writer_id=writer_id, 
                    create_datetime=create_datetime, 
                    title=title, content=content,
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
    def get_ongoing_list(self, start_cursor: datetime|None) -> tuple[List[Vote], bool, datetime]:

        #커서가 none이면 가장 최신 것부터 40개
        if cursor is None:
            cursor = datetime.now(timezone.utc)

        #생성 시간이 커서보다 최신인 것부터 오름차순(최신순)으로 40개 리턴
        query = (
            select(Vote)
            .where(Vote.create_datetime < cursor)
            .order_by(Vote.create_datetime.asc())
            .limit(40)
        )

        results = self.session.execute(query).scalars().all()

        #다음 커서는 40개 중 가장 과거에 생성된 것
        next_cursor = results[-1].create_datetime if results else None

        #만약 40개를 꽉 채웠다면 추가 내용이 있을 가능성 있음
        has_next = len(results) == 40
        
        return results, has_next, next_cursor

    # 투표글 상세 내용 조회
    def get_vote_by_vote_id(self, vote_id: int) -> Vote:
        return self.session.scalar(select(Vote).where(Vote.id == vote_id))
    

    #투표 참여하기
    def participate_vote(self, vote: Vote, user_id: int, choice_id_list: List[int]) -> None:

        # 참여하려고 하는 투표에 이미 투표를 한 상태라면 이전 선택지 참여는 제거하기
        for choice in vote.choices:
            choice_participation = self.session.scalar(
                select(ChoiceParticipation).where((ChoiceParticipation.choice_id == choice.id) & (ChoiceParticipation.user_id == user_id)))
            
            if choice_participation is not None:
                self.session.delete(choice_participation)
        
        self.session.flush()

        # 선택한 선택지 생성하기
        for choice_id in choice_id_list:
            choice_participation = ChoiceParticipation(user_id=user_id, choice_id=choice_id)
            self.session.add(choice_participation)

        self.session.commit()
        return vote
    
    def create_comment(self, vote_id: int, writed_id: int, content: str) -> Vote:
        comment = Comment(vote_id=vote_id, writer_id=writed_id, content=content,
                          create_datetime=datetime.now(timezone.utc),
                          is_edited=False)
        self.session.add(comment)
        self.session.commit()

    def get_comment_by_comment_id(self, comment_id: int) -> Comment:
        return self.session.scalar(select(Comment).where(Comment.id == comment_id))
    
    def edit_comment_content(self, comment_id: int, comment_content: str) -> None:
        comment = self.get_comment_by_comment_id(comment_id)
        comment.content = comment_content
        comment.is_edited = True
        comment.edited_datetime = datetime.now(timezone.utc)
        self.session.commit()

    def delete_comment_by_comment_id(self, comment_id: int) -> None:
        comment = self.get_comment_by_comment_id(comment_id)

        # is_deleted = True로 바꾸고, deleted_datetime을 기록
        comment.is_deleted = True
        comment.deleted_datetime = datetime.now(timezone.utc)
        self.session.commit()