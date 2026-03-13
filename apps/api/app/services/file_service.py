"""
파일 업로드 서비스
Presigned URL 발급 및 Attachment 레코드 관리
"""
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment


class MockStorageAdapter:
    """스토리지 어댑터 placeholder (Phase 2에서 S3/GCS 연동)"""

    @staticmethod
    async def generate_presigned_url(
        file_key: str,
        file_type: str,
        expires_in: int = 3600,
    ) -> dict[str, str]:
        return {
            "upload_url": f"https://storage.example.com/upload/{file_key}?expires={expires_in}",
            "file_key": file_key,
            "file_url": f"https://storage.example.com/files/{file_key}",
        }


_storage = MockStorageAdapter()


async def presign_upload(
    file_name: str,
    file_type: str,
    related_table: str,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> dict[str, Any]:
    """
    Presigned URL 발급
    1. 파일 키 생성
    2. MockStorage에서 URL 발급
    3. Attachment 레코드 생성 (status: pending)
    4. 응답 반환
    """
    file_key = f"{related_table}/{uuid.uuid4()}/{file_name}"

    presign_result = await _storage.generate_presigned_url(
        file_key=file_key,
        file_type=file_type,
    )

    attachment = Attachment(
        file_name=file_name,
        file_key=file_key,
        file_type=file_type,
        file_url=presign_result["file_url"],
        related_table=related_table,
        uploaded_by=actor_user_id,
    )
    db.add(attachment)
    await db.flush()

    return {
        "attachment_id": str(attachment.id),
        "upload_url": presign_result["upload_url"],
        "file_key": file_key,
        "file_url": presign_result["file_url"],
    }
