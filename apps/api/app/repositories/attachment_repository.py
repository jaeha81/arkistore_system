"""
첨부파일 리포지토리
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment
from app.repositories.base import BaseRepository


class AttachmentRepository(BaseRepository[Attachment]):
    model = Attachment

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_file_key(self, file_key: str) -> Attachment | None:
        stmt = select(Attachment).where(Attachment.file_key == file_key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_related(self, related_table: str, related_id: UUID) -> list[Attachment]:
        stmt = select(Attachment).where(
            Attachment.related_table == related_table,
            Attachment.related_id == related_id,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
