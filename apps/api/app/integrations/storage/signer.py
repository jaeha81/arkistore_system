"""
파일 업로드용 Presigned URL 생성
S3 호환 스토리지 지원
"""
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PresignResult:
    upload_url: str
    file_key: str
    attachment_id: uuid.UUID


class BaseStorageSigner(ABC):
    @abstractmethod
    async def generate_presign(
        self,
        file_name: str,
        file_type: str,
        related_table: str,
    ) -> PresignResult:
        ...


class S3StorageSigner(BaseStorageSigner):
    """실제 S3 Presigned URL 생성 (Phase 1에서 구현)"""

    def __init__(self, bucket: str, region: str, access_key: str, secret_key: str):
        import boto3
        self.s3 = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self.bucket = bucket

    async def generate_presign(
        self,
        file_name: str,
        file_type: str,
        related_table: str,
    ) -> PresignResult:
        attachment_id = uuid.uuid4()
        file_key = f"{related_table}/{attachment_id}/{file_name}"

        upload_url = self.s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket,
                "Key": file_key,
                "ContentType": file_type,
            },
            ExpiresIn=3600,
        )
        return PresignResult(
            upload_url=upload_url,
            file_key=file_key,
            attachment_id=attachment_id,
        )


class MockStorageSigner(BaseStorageSigner):
    """테스트/개발용 Mock"""

    async def generate_presign(
        self,
        file_name: str,
        file_type: str,
        related_table: str,
    ) -> PresignResult:
        attachment_id = uuid.uuid4()
        file_key = f"{related_table}/{attachment_id}/{file_name}"
        return PresignResult(
            upload_url=f"https://mock-storage.local/upload/{file_key}?mock=true",
            file_key=file_key,
            attachment_id=attachment_id,
        )


def get_storage_signer() -> BaseStorageSigner:
    from app.core.config import settings

    if settings.STORAGE_BUCKET and settings.STORAGE_ACCESS_KEY:
        return S3StorageSigner(
            bucket=settings.STORAGE_BUCKET,
            region=settings.STORAGE_REGION,
            access_key=settings.STORAGE_ACCESS_KEY,
            secret_key=settings.STORAGE_SECRET_KEY,
        )
    return MockStorageSigner()
