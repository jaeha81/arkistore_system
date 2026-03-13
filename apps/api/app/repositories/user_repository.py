"""
사용자 리포지토리
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_id(self, id: UUID) -> User | None:
        stmt = select(User).where(User.id == id, User.is_active.is_(True), User.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
