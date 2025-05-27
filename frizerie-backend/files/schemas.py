from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from .models import FileType

class FileBase(BaseModel):
    is_public: bool = False

class FileCreate(FileBase):
    pass

class FileUpdate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_type: FileType
    mime_type: str
    size: int
    path: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FileInfo(BaseModel):
    filename: str
    content_type: str
    size: int
    url: str

class FileUploadResponse(BaseModel):
    message: str
    file_info: FileInfo

class FileListResponse(BaseModel):
    files: List[FileInfo] 