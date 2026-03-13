"""
파일 업로드 API 라우터
"""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import success_response
from app.services import file_service

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/presign", status_code=status.HTTP_201_CREATED)
async def presign_upload(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Presigned URL 발급"""
    body = await request.json()
    result = await file_service.presign_upload(
        file_name=body["file_name"],
        file_type=body["file_type"],
        related_table=body["related_table"],
        db=db,
        actor_user_id=current_user["id"],
    )
    return success_response(
        data=result,
        request_id=getattr(request.state, "request_id", None),
    )
