from fastapi import APIRouter

from snuvote.app.user.views import user_router
from snuvote.app.vote.views import vote_router
from snuvote.app.image.views import image_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(vote_router, prefix="/votes", tags=["votes"])
api_router.include_router(image_router, prefix="/images", tags=["images"])