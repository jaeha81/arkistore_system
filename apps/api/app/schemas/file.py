"""
파일 업로드 스키마
"""
from uuid import UUID

from pydantic import BaseModel


class FilePresignRequest(BaseModel):
    file_name: str
    file_type: str
    related_table: str


class FilePresignResponse(BaseModel):
    upload_url: str
    file_key: str
    attachment_id: UUID
