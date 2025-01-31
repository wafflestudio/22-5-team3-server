from functools import cache
from typing import Annotated, List
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from snuvote.database.models import Vote, Choice, ChoiceParticipation, Comment, VoteImage
import sys

from snuvote.database.connection import get_db_session
from sqlalchemy import func, select
from sqlalchemy import select, delete
from sqlalchemy.orm import Session, aliased, joinedload, Load, subqueryload

KST = timezone(timedelta(hours=9), "KST")

class VoteStore:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session
        self.pagination_size = 10
    

    #투표 추가하기
    async def add_vote(self,
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
        await self.session.flush()

        for choice_content_input in choices:
            choice = Choice(vote_id=vote.id,
                            choice_content = choice_content_input)
            self.session.add(choice)
        
        await self.session.flush()

        return vote
    
    async def add_vote_image(self, vote_id: int, image_order: int, image_src: str):
        new_voteimage = VoteImage(vote_id = vote_id,
                                  order=image_order,
                                  src = image_src)
        
        self.session.add(new_voteimage)
        await self.session.flush()

    # 진행 중인 투표 리스트 조회
    def get_ongoing_list(self, start_cursor: tuple[datetime,int] |None) -> tuple[List[tuple[Vote,int]], bool, tuple[datetime, int]|None]:

        #커서가 none이면 가장 최신 것부터 self.pagination_size개
        if start_cursor is None:
            start_cursor = (datetime.now(timezone.utc), 0)

        # 생성 시간이 커서보다 최신인 것부터 오름차순(최신순)으로 self.pagination_size개 리턴
        # 먼저 진행 중인 투표글의 Vote.id만 반환
        filtered_votes = (
            select(Vote.id)
            .where(
                (Vote.create_datetime < start_cursor[0])   # 생성 시간이 커서보다 과거이거나
                | (
                    (Vote.create_datetime == start_cursor[0]) & (Vote.id > start_cursor[1]) # 생성 시간이 커서와 같은데 id가 더 큰 경우
                )
            )
            .where(Vote.end_datetime > datetime.now(timezone.utc))
            .subquery()
        )

        # 현재 진행 중인 투표글 vote.id(filtered_votes)별 참여자 수를 구하는 서브 쿼리
        subquery = (
            select(
                Choice.vote_id.label("vote_id"),
                func.count(func.distinct(ChoiceParticipation.user_id)).label("participant_count")
            )
            .join(ChoiceParticipation, Choice.id == ChoiceParticipation.choice_id, isouter=True) # 참여가 없는 투표의 경우도 참여자 수는 반환되어야 하므로 left outer join
            .where(Choice.vote_id.in_(select(filtered_votes.c.id)))  # 필요한 투표만 선택
            .group_by(Choice.vote_id)
            .subquery()
        )

        # 메인 쿼리: 현재 진행 중인 투표글들만 Vote 정보 + 참여자 수 inner join
        query = (
            select(Vote, subquery.c.participant_count)
            .join(subquery, Vote.id == subquery.c.vote_id) # filtered_votes의 vote 정보와 참여자 수만 표시되어야 하므로 inner join
            .order_by(Vote.create_datetime.desc(), Vote.id.asc())
            .limit(self.pagination_size)
        )

        results = self.session.execute(query).all()

        #만약 self.pagination_size개를 꽉 채웠다면 추가 내용이 있을 가능성 있음
        has_next = len(results) == self.pagination_size
        
        #다음 커서는 self.pagination_size개 중 가장 과거에 생성된 것
        next_cursor = (results[-1][0].create_datetime, results[-1][0].id) if has_next else None
        
        return results, has_next, next_cursor


    # 완료된 투표글 리스트 조회
    async def get_ended_votes_list(self, start_cursor: tuple[datetime,int] |None) -> tuple[List[tuple[Vote,int]], bool, tuple[datetime, int]|None]:

        # 필터 쿼리: 완료된 투표글의 Vote.id만 반환
        # 커서가 none이면 가장 최근에 끝난 투표부터 최근에 끝난 순으로 self.pagination_size개
        if start_cursor is None:
            filtered_votes = (
                select(Vote.id)
                .where(Vote.end_datetime < datetime.now(timezone.utc))
                .subquery()
            )
        else: # 커서가 None이 아니면 커서보다 과거에 끝난 투표부터 최근에 끝난 순으로 self.pagination_size개
            filtered_votes = (
                select(Vote.id)
                .where(Vote.end_datetime <= datetime.now(timezone.utc))
                .where(
                    (Vote.end_datetime < start_cursor[0])  # 종료시간이 커서 시간보다 과거이거나
                    | (
                        (Vote.end_datetime == start_cursor[0]) & (Vote.id > start_cursor[1]) # 종료시간이 커서와 같은데 id가 더 큰 경우
                    )
                )
                .subquery()
            )
        
        #서브 쿼리: filtered_votes의 vote_id별 참가자 수를 구하는 서브 쿼리
        subquery = (
            select(
                Choice.vote_id.label("vote_id"),
                func.count(func.distinct(ChoiceParticipation.user_id)).label("participant_count")
            )
            .join(ChoiceParticipation, Choice.id == ChoiceParticipation.choice_id, isouter=True) # 참여가 없는 투표의 경우도 참여자 수는 반환되어야 하므로 left outer join
            .where(Choice.vote_id.in_(select(filtered_votes.c.id)))  # 필요한 투표만 선택
            .group_by(Choice.vote_id)
            .subquery()
        )

        # 메인 쿼리: 완료된 투표글들만 Vote 정보 + 참여자 수 inner join
        query = (
            select(Vote, subquery.c.participant_count)
            .options(
                subqueryload(Vote.choices).subqueryload(Choice.choice_participations),
                subqueryload(Vote.images)
            )
            .join(subquery, Vote.id == subquery.c.vote_id) # filtered_votes의 vote 정보와 참여자 수만 표시되어야 하므로 inner join
            .order_by(Vote.end_datetime.desc(), Vote.id.asc())
            .limit(self.pagination_size)

        )

        results = await self.session.execute(query)
        results = results.all()

        # 만약 self.pagination_size개를 꽉 채웠다면 추가 내용이 있을 가능성 있음
        has_next = len(results) == self.pagination_size
        
        # 다음 커서는 self.pagination_size개 중 가장 과거에 완료된 것
        next_cursor = (results[-1][0].end_datetime, results[-1][0].id) if has_next else None
        
        return results, has_next, next_cursor


    def get_hot_votes_list(self, start_cursor: tuple[datetime,int] |None) ->  tuple[List[tuple[Vote,int]], bool, tuple[datetime, int]|None]:

        #커서가 none이면 가장 최신 것부터 self.pagination_size개
        if start_cursor is None:
            start_cursor = (datetime.now(timezone.utc), 0)
        

        # 먼저 필요한 Vote만 필터링
        filtered_votes = (
            select(Vote.id)
            .where(
                (Vote.create_datetime < start_cursor[0])   # 생성 시간이 커서보다 과거이거나
                | (
                    (Vote.create_datetime == start_cursor[0]) & (Vote.id > start_cursor[1]) # 생성 시간이 커서와 같은데 id가 더 큰 경우
                )
            )
            .subquery()
        )

        #서브 쿼리
        subquery = (
            select(
                Choice.vote_id.label("vote_id"),
                func.count(func.distinct(ChoiceParticipation.user_id)).label("participant_count")
            )
            .join(ChoiceParticipation, Choice.id == ChoiceParticipation.choice_id)
            .where(Choice.vote_id.in_(select(filtered_votes.c.id)))  # 필요한 투표만 선택
            .group_by(Choice.vote_id)
            .subquery()
        )

        #메인 쿼리
        query = (
            select(Vote, subquery.c.participant_count)
            .join(subquery, Vote.id == subquery.c.vote_id)
            .where(subquery.c.participant_count >= 5)  # 참여자 수 5명 이상 조건
            .order_by(Vote.create_datetime.desc(), Vote.id.asc())
            .limit(self.pagination_size)
        )

        # results : 투표 리스트
        results = self.session.execute(query).all()

        #만약 self.pagination_size개를 꽉 채웠다면 추가 내용이 있을 가능성 있음
        has_next = len(results) == self.pagination_size
        
        #다음 커서는 self.pagination_size개 중 가장 과거에 생성된 것
        next_cursor = (results[-1][0].create_datetime, results[-1][0].id) if has_next else None
        
        return results, has_next, next_cursor


    #내가 만든 투표글 리스트
    def get_my_votes_list(self, user_id: int, start_cursor: tuple[datetime,int] |None) ->  tuple[List[tuple[Vote,int]], bool, tuple[datetime, int]|None]:

        #커서가 none이면 가장 최신 것부터 self.pagination_size개
        if start_cursor is None:
            start_cursor = (datetime.now(timezone.utc), 0)
        

        # 먼저 내가 만든 Vote만 필터링
        filtered_votes = (
            select(Vote.id)
            .where(
                (Vote.create_datetime < start_cursor[0])   # 생성 시간이 커서보다 과거이거나
                | (
                    (Vote.create_datetime == start_cursor[0]) & (Vote.id > start_cursor[1]) # 생성 시간이 커서와 같은데 id가 더 큰 경우
                )
            )
            .where(Vote.writer_id == user_id)
            .subquery()
        )

        #서브 쿼리: filtered_votes의 vote_id별 참가자 수를 구하는 서브 쿼리
        subquery = (
            select(
                Choice.vote_id.label("vote_id"),
                func.count(func.distinct(ChoiceParticipation.user_id)).label("participant_count")
            )
            .join(ChoiceParticipation, Choice.id == ChoiceParticipation.choice_id, isouter=True) # 참여가 없는 투표의 경우도 참여자 수는 반환되어야 하므로 left outer join
            .where(Choice.vote_id.in_(select(filtered_votes.c.id)))  # 필요한 투표만 선택
            .group_by(Choice.vote_id)
            .subquery()
        )

        # 메인 쿼리: 완료된 투표글들만 Vote 정보 + 참여자 수 inner join
        query = (
            select(Vote, subquery.c.participant_count)
            .join(subquery, Vote.id == subquery.c.vote_id) # filtered_votes의 vote 정보와 참여자 수만 표시되어야 하므로 inner join
            .order_by(Vote.create_datetime.desc(), Vote.id.asc())
            .limit(self.pagination_size)
        )

        # results : 투표 리스트
        results = self.session.execute(query).all()

        #만약 self.pagination_size개를 꽉 채웠다면 추가 내용이 있을 가능성 있음
        has_next = len(results) == self.pagination_size
        
        #다음 커서는 self.pagination_size개 중 생성 시간이 가장 과거인 것
        next_cursor = (results[-1][0].create_datetime, results[-1][0].id) if has_next else None
        
        return results, has_next, next_cursor
    

    #내가 참여한 투표글 리스트
    def get_participated_votes_list(self, user_id: int, start_cursor: tuple[datetime,int] |None) ->  tuple[List[tuple[Vote,int]], bool, tuple[datetime, int]|None]:

        #커서가 none이면 가장 최신 것부터 self.pagination_size개
        if start_cursor is None:
            start_cursor = (datetime.now(timezone.utc), 0)
        

        # 먼저 내가 참여한 Vote만 필터링
        filtered_votes = (
            select(Vote.id)
            .join(ChoiceParticipation, ChoiceParticipation.choice_id == Choice.id)
            .join(Choice, Choice.vote_id == Vote.id)
            .where(ChoiceParticipation.user_id == user_id)
            .where(
                (Vote.create_datetime < start_cursor[0])   # 생성 시간이 커서보다 과거이거나
                | (
                    (Vote.create_datetime == start_cursor[0]) & (Vote.id > start_cursor[1]) # 생성 시간이 커서와 같은데 id가 더 큰 경우
                )
            )
            .subquery()
        )

        #서브 쿼리: filtered_votes의 vote_id별 참가자 수를 구하는 서브 쿼리
        subquery = (
            select(
                Choice.vote_id.label("vote_id"),
                func.count(func.distinct(ChoiceParticipation.user_id)).label("participant_count")
            )
            .join(ChoiceParticipation, Choice.id == ChoiceParticipation.choice_id, isouter=True) # 참여가 없는 투표의 경우도 참여자 수는 반환되어야 하므로 left outer join
            .where(Choice.vote_id.in_(select(filtered_votes.c.id)))  # 필요한 투표만 선택
            .group_by(Choice.vote_id)
            .subquery()
        )

        # 메인 쿼리: 완료된 투표글들만 Vote 정보 + 참여자 수 inner join
        query = (
            select(Vote, subquery.c.participant_count)
            .join(subquery, Vote.id == subquery.c.vote_id) # filtered_votes의 vote 정보와 참여자 수만 표시되어야 하므로 inner join
            .order_by(Vote.create_datetime.desc(), Vote.id.asc())
            .limit(self.pagination_size)
        )

        # results : 투표 리스트
        results = self.session.execute(query).all()

        #만약 self.pagination_size개를 꽉 채웠다면 추가 내용이 있을 가능성 있음
        has_next = len(results) == self.pagination_size
        
        #다음 커서는 self.pagination_size개 중 생성 시간이 가장 과거인 것
        next_cursor = (results[-1][0].create_datetime, results[-1][0].id) if has_next else None
        
        return results, has_next, next_cursor


    # 투표글 상세 내용 조회
    async def get_vote_by_vote_id(self, vote_id: int) -> Vote:
        return await self.session.scalar(select(Vote).options(joinedload(Vote.writer), joinedload(Vote.choices).joinedload(Choice.choice_participations).joinedload(ChoiceParticipation.user), joinedload(Vote.comments).joinedload(Comment.writer), joinedload(Vote.images)).where(Vote.id == vote_id))
    

    #투표 참여하기
    async def participate_vote(self, vote: Vote, user_id: int, choice_id_list: List[int]) -> None:

        # 참여하려고 하는 투표에 이미 투표를 한 상태라면 이전 선택지 참여는 제거하기
        for choice in vote.choices:
            choice_participation = await self.session.scalar(
                select(ChoiceParticipation).where((ChoiceParticipation.choice_id == choice.id) & (ChoiceParticipation.user_id == user_id)))
            
            if choice_participation is not None:
                await self.session.delete(choice_participation)
        
        await self.session.flush()

        # 선택한 선택지 생성하기
        for choice_id in choice_id_list:
            choice_participation = ChoiceParticipation(user_id=user_id, choice_id=choice_id)
            self.session.add(choice_participation)

        await self.session.commit()
        self.session.expire_all()
    
    #투표 조기 종료하기
    async def close_vote(self, vote_id: int) -> None:
        vote = await self.get_vote_by_vote_id(vote_id)
        vote.end_datetime = datetime.now(timezone.utc)
        self.session.commit()
    
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
