"""
API 공통 의존성: DB 세션, 현재 사용자, 역할 검증
"""
import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.enums import UserRole
from app.core.security import decode_token, get_token_from_cookie, get_token_from_header
from app.models.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """DB 세션 주입"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    현재 인증 사용자 추출
    1. 쿠키 → Bearer 헤더 순으로 토큰 검색
    2. JWT 디코드
    3. DB에서 사용자 로드
    4. user dict 반환
    """
    token = get_token_from_cookie(request) or get_token_from_header(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = decode_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    stmt = select(User).where(User.id == user_id, User.is_active.is_(True))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }


def require_role(*roles: UserRole):
    """특정 역할 중 하나를 요구하는 dependency factory"""

    async def _checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_role = current_user.get("role")
        allowed = [r.value if isinstance(r, UserRole) else r for r in roles]
        if user_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return current_user

    return _checker
