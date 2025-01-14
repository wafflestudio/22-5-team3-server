from typing import Annotated, List

from fastapi import Depends
from snuvote.database.models import Vote, User, Choice, ChoiceParticipation, Comment
from snuvote.app.vote.store import VoteStore
from snuvote.app.vote.errors import ChoiceNotFoundError, InvalidFieldFormatError, MultipleChoicesError, ParticipationCodeError, ParticipationCodeNotProvidedError, WrongParticipationCodeError, EndedVoteError, CommentNotYoursError, CommentNotInThisVoteError
from snuvote.app.vote.dto.requests import ParticipateVoteRequest, CommentRequest

from datetime import datetime, timedelta, timezone



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
    
    def participate_vote(self, vote: Vote, user: User, participate_vote_request: ParticipateVoteRequest) -> None:
        # 종료 시간 이후인 경우
        if datetime.now(tz=timezone.utc) > vote.end_datetime.replace(tzinfo=timezone.utc): 
            raise EndedVoteError()
        
        # 참여코드가 필요한 투표글인 경우
        if vote.participation_code_required:
            # 프론트에서 제공되지 않은 경우
            if not participate_vote_request.participation_code:
                raise ParticipationCodeNotProvidedError()
            # 참여코드가 불일치하는 경우
            if vote.participation_code != participate_vote_request.participation_code:
                raise WrongParticipationCodeError()
        
        # 중복 투표 불가능인데 중복 투표 했을 때
        if not vote.multiple_choice and len(participate_vote_request.participated_choice_ids) > 1:
            raise MultipleChoicesError()
        
        # 해당 vote에 Request된 choice_id에 해당하는 선택지가 존재하지 않는 경우
        vote_choice_id_list = [choice.id for choice in vote.choices]
        for choice_id in participate_vote_request.participated_choice_ids:
            if choice_id not in vote_choice_id_list:
                raise ChoiceNotFoundError()

        user_id = user.id
        choice_id_list = participate_vote_request.participated_choice_ids

        return self.vote_store.participate_vote(vote=vote, user_id=user_id, choice_id_list=choice_id_list)
    
    def create_comment(self, vote: Vote, user: User, comment_request: CommentRequest) -> None:
        self.vote_store.create_comment(vote_id=vote.id, writed_id=user.id, content=comment_request.content)
    
    def get_comment_by_comment_id(self, comment_id:int) -> Comment:
        return self.vote_store.get_comment_by_comment_id(comment_id)


    def edit_comment(self, user: User, vote: Vote, comment: Comment, comment_request: CommentRequest) -> None:

        # 만약 해당 Comment가 해당 Vote에 속하는 것이 아닐 경우
        if comment.vote_id != vote.id:
            raise CommentNotInThisVoteError()

        # 해당 Comment가 해당 User의 것이 아닌 경우
        if comment.writer_id != user.id:
            raise CommentNotYoursError()

        
        # 해당 comment_content 수정
        self.vote_store.edit_comment_content(
            comment_id = comment.id,
            comment_content = comment_request.content
        )

    def delete_comment(self, user: User, vote: Vote, comment: Comment) -> None:
        # 만약 해당 Comment가 해당 Vote에 속하는 것이 아닐 경우
        if comment.vote_id != vote.id:
            raise CommentNotInThisVoteError()

        # 해당 Comment가 해당 User의 것이 아닌 경우
        if comment.writer_id != user.id:
            raise CommentNotYoursError()
    
        # 해당 Comment를 삭제
        self.vote_store.delete_comment_by_comment_id(comment_id = comment.id)