from fastapi import APIRouter
from fastapi.responses import FileResponse

image_router = APIRouter()

@image_router.get("/{image_name}")
def get_image(image_name: str) -> FileResponse:
    return FileResponse(f'./images/{image_name}')