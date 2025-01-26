from typing import Annotated, List

from fastapi import Depends, UploadFile 
from snuvote.database.models import Vote, User, Choice, ChoiceParticipation, Comment
from snuvote.app.vote.store import VoteStore
from snuvote.app.vote.errors import ChoiceNotFoundError, VoteNotYoursError, MultipleChoicesError, ParticipationCodeError, ParticipationCodeNotProvidedError, WrongParticipationCodeError, EndedVoteError, CommentNotYoursError, CommentNotInThisVoteError, InvalidFileExtensionError
from snuvote.app.vote.dto.requests import ParticipateVoteRequest, CommentRequest

from datetime import datetime, timedelta, timezone

import secrets
import os
import boto3
from botocore.config import Config


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

class VoteService:
    def __init__(self, vote_store: Annotated[VoteStore, Depends()]) -> None:
        self.vote_store = vote_store
    
    def upload_vote_images(self, vote: Vote, images: List[UploadFile]) -> None:
        # voteimage를 저장하고 DB에 정보를 저장하는 함수

        # S3 client 생성
        s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_S3_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_S3_SECRET_ACCESS_KEY'), config=Config(region_name=os.getenv('AWS_DEFAULT_REGION')))

        image_order = 0 # VoteImage.order에 저장될 이미지 순서 번호

        for image in images:
            image_order += 1
            image_name = f'{secrets.token_urlsafe(16)}.{image.filename.split(".")[-1]}' # 파일이름 = {랜덤문자열}.{확장자}
            image_path = f'voteimages/{image_name}' # S3 버킷 내 파일 경로: voteimages/{파일이름}

            # S3 버킷 해당 경로에 업로드
            s3.upload_fileobj(image.file, os.getenv('AWS_S3_BUCKET_NAME'), image_path)

            # S3 버킷에 업로드된 이미지 경로
            image_src = f'https://{os.getenv("AWS_S3_BUCKET_NAME")}.s3.{os.getenv("AWS_DEFAULT_REGION")}.amazonaws.com/{image_path}'

            # VoteImage 테이블에 이미지 정보 저장
            self.vote_store.add_vote_image(vote_id=vote.id, image_order=image_order, image_src=image_src)


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
                 choices: List[str],
                 images: List[UploadFile]|None) -> Vote:

        #참여코드가 필요한데 참여코드가 없을 경우 400 에러
        if participation_code_required and not participation_code:
            raise ParticipationCodeError()
        
        # 투표 추가
        vote = self.vote_store.add_vote(writer_id=writer_id,
                                        title=title,
                                        content=content, 
                                        participation_code_required=participation_code_required,
                                        participation_code=participation_code, 
                                        realtime_result=realtime_result, 
                                        multiple_choice=multiple_choice, 
                                        annonymous_choice=annonymous_choice, 
                                        end_datetime=end_datetime,
                                        choices=choices)
        
        # 이미지 업로드
        if images:
            # 확장자가 안 맞으면 오류
            for image in images:
                filename = image.filename
                extension = filename.split(".")[-1].lower()  # 확장자 추출 및 소문자로 변환
                if extension not in ALLOWED_EXTENSIONS:
                    raise InvalidFileExtensionError
            self.upload_vote_images(vote, images)

        return self.vote_store.get_vote_by_vote_id(vote_id=vote.id)


    # 진행 중인 투표 리스트 조회
    def get_ongoing_list(self, start_cursor: tuple[datetime, int]) -> tuple[List[tuple[Vote,int]], bool, datetime|None]:
        return self.vote_store.get_ongoing_list(start_cursor)
    
    # 완료된 투표글 리스트 조회
    def get_ended_votes_list(self, start_cursor: tuple[datetime, int]) -> tuple[List[tuple[Vote,int]], bool, datetime|None]:
        return self.vote_store.get_ended_votes_list(start_cursor)
    
    # HOT 투표글 리스트 조회
    def get_hot_votes_list(self, start_cursor: tuple[datetime, int]) -> tuple[List[tuple[Vote,int]], bool, datetime|None]:
        return self.vote_store.get_hot_votes_list(start_cursor)
    
    # 내가 만든 투표 리스트 조회
    def get_my_votes_list(self, user: User, start_cursor: tuple[datetime, int]) -> tuple[List[tuple[Vote,int]], bool, datetime|None]:
        return self.vote_store.get_my_votes_list(user.id, start_cursor)
    
    def get_participated_votes_list(self, user: User, start_cursor: tuple[datetime, int]) -> tuple[List[tuple[Vote,int]], bool, datetime|None]:
        return self.vote_store.get_participated_votes_list(user.id, start_cursor)

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
    
    #투표 조기 종료하기
    def close_vote(self, vote:Vote, user: User)-> None:

        #만약 투표 작성자가 아닐 경우
        if vote.writer_id != user.id:
            raise VoteNotYoursError()
        
        if vote.end_datetime <= datetime.now(tz=timezone.utc).replace(tzinfo=None):
            raise EndedVoteError()
        
        self.vote_store.close_vote(vote_id=vote.id)
    
    
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