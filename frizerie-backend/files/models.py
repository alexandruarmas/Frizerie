from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from enum import Enum
from config.database import Base

class FileType(str, Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    OTHER = "other"

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)  # Size in bytes
    path = Column(String, nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="files")
    
    def __repr__(self):
        return f"<File {self.id}: {self.original_filename}>" 