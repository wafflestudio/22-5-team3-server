from typing import Annotated, List
from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.security import HTTPBearer

from pydantic.functional_validators import AfterValidator
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

from snuvote.app.vote.dto.requests import CreateVoteRequest, ParticipateVoteRequest, CommentRequest
from snuvote.app.vote.dto.responses import OnGoingVotesListResponse, VotesListInfoResponse, VoteDetailResponse, ChoiceDetailResponse, CommentDetailResponse
from snuvote.app.vote.errors import VoteNotFoundError, ChoiceNotFoundError, CommentNotFoundError, InvalidVoteListCategoryError, CursorError
from datetime import datetime, timedelta, timezone

from snuvote.database.models import User
from snuvote.app.vote.service import VoteService
from snuvote.app.vote.errors import InvalidFieldFormatError
from snuvote.app.user.views import login_with_access_token

vote_router = APIRouter()

security = HTTPBearer()


#create vote
@vote_router.post("/create", status_code=HTTP_201_CREATED)
async def create_vote(
    user: Annotated[User, Depends(login_with_access_token)],
    vote_service: Annotated[VoteService, Depends()],
    images: List[UploadFile]|None = File(None),
    create_vote_json = Form(media_type="multipart/form-data", json_schema_extra=CreateVoteRequest.model_json_schema())
):
    
    create_vote_request = CreateVoteRequest.model_validate_json(create_vote_json)

    
    vote = await vote_service.add_vote(
        writer_id=user.id,
        title=create_vote_request.title,
        content=create_vote_request.content,
        participation_code_required=create_vote_request.participation_code_required,
        participation_code=create_vote_request.participation_code,
        realtime_result=create_vote_request.realtime_result,
        multiple_choice=create_vote_request.multiple_choice,
        annonymous_choice=create_vote_request.annonymous_choice,
        end_datetime=create_vote_request.end_datetime,
        choices=create_vote_request.choices,
        images = images
    )

    return await get_vote(vote.id, user, vote_service)




# 완료된/진행중인/hot 투표글 조회
@vote_router.get("/list", status_code=HTTP_200_OK)
async def get_votes_list(
    user: Annotated[User, Depends(login_with_access_token)],
    vote_service: Annotated[VoteService, Depends()],
    category: str,
    start_cursor_time: datetime|None = None,
    start_cursor_id: int|None = None
):
    start_cursor: tuple[datetime, int]|None = None

    if start_cursor_time is not None and start_cursor_id is not None:
        start_cursor = (start_cursor_time, start_cursor_id)
    elif start_cursor_time is not None or start_cursor_id is not None:
        raise CursorError()


    if category == "ended":
        results, has_next, next_cursor = await vote_service.get_ended_votes_list(start_cursor)
    elif category == "ongoing":
        results, has_next, next_cursor = await vote_service.get_ongoing_list(start_cursor)
    elif category == "hot":
        results, has_next, next_cursor = await vote_service.get_hot_votes_list(start_cursor)
    elif category == "made":
        results, has_next, next_cursor = await vote_service.get_my_votes_list(user, start_cursor)
    elif category == "participated":
        results, has_next, next_cursor = await vote_service.get_participated_votes_list(user, start_cursor)
    else: raise InvalidVoteListCategoryError()

    return OnGoingVotesListResponse(
        votes_list = [ VotesListInfoResponse.from_vote_user(vote, user, participant_count) for vote, participant_count in results ],
        has_next = has_next,
        next_cursor_time = next_cursor[0] if next_cursor else None,
        next_cursor_id = next_cursor[1] if next_cursor else None
    )

# 특정 투표글 정보 조회
@vote_router.get("/{vote_id}", status_code=HTTP_200_OK)
async def get_vote(
    vote_id: int,
    user: Annotated[User, Depends(login_with_access_token)],
    vote_service: Annotated[VoteService, Depends()]
):
    # 해당 vote_id에 해당하는 투표글 조회
    vote = await vote_service.get_vote_by_vote_id(vote_id = vote_id)
    # 해당 vote_id에 해당하는 투표글이 없을 경우 404 Not Found
    if not vote:
        raise VoteNotFoundError()
    
    #투표 생성자 아이디와 유저 아이디가 같은 경우
    is_writer = vote.writer_id == user.id

    return VoteDetailResponse(
        vote_id = vote.id,
        writer_name = vote.writer.name,
        is_writer= is_writer,
        title = vote.title,
        content = vote.content,
        participation_code_required = vote.participation_code_required,
        realtime_result = vote.realtime_result,
        multiple_choice = vote.multiple_choice,
        annonymous_choice = vote.annonymous_choice,
        create_datetime = vote.create_datetime,
        end_datetime = vote.end_datetime,
        choices= [ChoiceDetailResponse.from_choice(choice, user, vote.annonymous_choice, vote.realtime_result, vote.end_datetime) for choice in vote.choices],
        comments = [CommentDetailResponse.from_comment_user(comment, user) for comment in vote.comments if comment.is_deleted==False],
        images = [image.src for image in vote.images],
        participant_count = VoteDetailResponse.get_participant_count_from_vote(vote)
    )


#투표 참여하기
@vote_router.post("/{vote_id}/participate", status_code=HTTP_201_CREATED)
async def participate_vote(
    vote_id: int,
    user: Annotated[User, Depends(login_with_access_token)],
    participate_vote_request: ParticipateVoteRequest,
    vote_service: Annotated[VoteService, Depends()]
):
    
    # 해당 vote_id에 해당하는 투표글 조회
    vote = await vote_service.get_vote_by_vote_id(vote_id = vote_id)

    # 해당 vote_id에 해당하는 투표글이 없을 경우 404 Not Found
    if not vote:
        raise VoteNotFoundError()

    #투표 참여하기
    await vote_service.participate_vote(vote, user, participate_vote_request)
    return await get_vote(vote_id, user, vote_service)

#투표 조기 종료하기
@vote_router.patch("/{vote_id}/close", status_code=HTTP_200_OK)
async def close_vote(
    vote_id: int,
    user: Annotated[User, Depends(login_with_access_token)],
    vote_service: Annotated[VoteService, Depends()]
):
    vote = await vote_service.get_vote_by_vote_id(vote_id = vote_id)

    # 해당 vote_id에 해당하는 투표글이 없을 경우 404 Not Found
    if not vote:
        raise VoteNotFoundError()
    
    await vote_service.close_vote(vote, user)

    return await get_vote(vote_id, user, vote_service)


# 댓글 추가하기
@vote_router.post("/{vote_id}/comment", status_code=HTTP_201_CREATED)
async def create_comment(
    vote_id: int,
    vote_service: Annotated[VoteService, Depends()],
    user: Annotated[User, Depends(login_with_access_token)],
    comment_request: CommentRequest
):
    # 해당 vote_id에 해당하는 투표글 조회
    vote = await vote_service.get_vote_by_vote_id(vote_id = vote_id)

    # 해당 vote_id에 해당하는 투표글이 없을 경우 404 Not Found
    if not vote:
        raise VoteNotFoundError()
    
    # 댓글 추가하기
    await vote_service.create_comment(vote, user, comment_request)

    return await get_vote(vote_id, user, vote_service)

# 댓글 수정하기
@vote_router.patch("/{vote_id}/comment/{comment_id}", status_code=HTTP_200_OK)
async def edit_comment(
    vote_id: int,
    comment_id: int,
    user: Annotated[User, Depends(login_with_access_token)],
    comment_request: CommentRequest,
    vote_service: Annotated[VoteService, Depends()]
):
    vote = await vote_service.get_vote_by_vote_id(vote_id)
    comment = await vote_service.get_comment_by_comment_id(comment_id)

    # 해당 vote_id에 해당하는 투표글이 없을 경우 404 Not Found
    if not vote:
        raise VoteNotFoundError()

    # 해당 comment에 해당하는 투표글이 없을 경우 404 Not Found
    if not comment:
        raise CommentNotFoundError()
    
    # 댓글 수정하기
    await vote_service.edit_comment(user, vote, comment, comment_request)
    
    return await get_vote(vote_id, user, vote_service)

# 댓글 삭제하기
@vote_router.delete("/{vote_id}/comment/{comment_id}", status_code=HTTP_200_OK)
async def delete_comment(
    vote_id: int,
    comment_id: int,
    user: Annotated[User, Depends(login_with_access_token)],
    vote_service: Annotated[VoteService, Depends()],
):
    vote = await vote_service.get_vote_by_vote_id(vote_id)
    comment = await vote_service.get_comment_by_comment_id(comment_id)

    # 해당 vote_id에 해당하는 투표글이 없을 경우 404 Not Found
    if not vote:
        raise VoteNotFoundError()

    # 해당 comment에 해당하는 투표글이 없을 경우 404 Not Found
    if not comment:
        raise CommentNotFoundError()
    
    await vote_service.delete_comment(user, vote, comment)

    return await get_vote(vote_id, user, vote_service)