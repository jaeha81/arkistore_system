"""
인증 API 라우터
"""
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import success_response
from app.core.security import clear_auth_cookies, set_auth_cookies
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """로그인 (인증 불필요)"""
    body = await request.json()
    email = body.get("email", "")
    password = body.get("password", "")

    user, access_token, refresh_token = await auth_service.login(email, password, db)

    set_auth_cookies(response, access_token, refresh_token)

    return success_response(
        data={
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
            },
            "access_token": access_token,
        },
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
):
    """로그아웃"""
    clear_auth_cookies(response)
    return success_response(
        data={"message": "Logged out"},
        request_id=getattr(request.state, "request_id", None),
    )


@router.get("/me")
async def get_me(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """현재 사용자 정보 조회"""
    user = await auth_service.get_me(current_user["id"], db)
    return success_response(
        data={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        request_id=getattr(request.state, "request_id", None),
    )
