"""
인증 서비스: 로그인, 현재 사용자 조회
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models.user import User


async def login(
    email: str,
    password: str,
    db: AsyncSession,
) -> tuple[User, str, str]:
    """이메일/비밀번호로 로그인 → (User, access_token, refresh_token)"""
    stmt = select(User).where(User.email == email, User.is_active.is_(True))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Invalid email or password")

    access_token = create_access_token(
        subject=str(user.id),
        extra={"role": user.role, "name": user.name},
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return user, access_token, refresh_token


async def get_me(
    user_id: uuid.UUID,
    db: AsyncSession,
) -> User:
    """현재 사용자 정보 조회"""
    stmt = select(User).where(User.id == user_id, User.is_active.is_(True))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("User not found or inactive")

    return user
