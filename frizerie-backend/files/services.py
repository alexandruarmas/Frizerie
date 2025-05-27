import os
import shutil
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import mimetypes

from .models import File, FileType
from .schemas import FileCreate
from errors.exceptions import NotFoundError, BusinessLogicError

# Configure upload directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Assuming a static directory is used for storage. 
# You might want to get the storage path from settings.
STORAGE_DIR = "static/uploads"

# Create the storage directory if it doesn't exist
os.makedirs(STORAGE_DIR, exist_ok=True)

def get_file_type(mime_type: str) -> FileType:
    """
    Determine file type from MIME type.
    """
    if mime_type.startswith("image/"):
        return FileType.IMAGE
    elif mime_type.startswith("application/"):
        return FileType.DOCUMENT
    return FileType.OTHER

async def upload_file(
    db: Session,
    file: UploadFile,
    user_id: int,
    is_public: bool = False
) -> File:
    """
    Upload a file and create a database record.
    """
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create user directory if it doesn't exist
        user_dir = os.path.join(UPLOAD_DIR, str(user_id))
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        # Save file
        file_path = os.path.join(user_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create database record
        db_file = File(
            user_id=user_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_type=get_file_type(file.content_type),
            mime_type=file.content_type,
            size=file_size,
            path=file_path,
            is_public=is_public
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return db_file
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise BusinessLogicError(f"File upload failed: {str(e)}")

async def download_file(db: Session, file_id: int) -> tuple[File, bytes]:
    """
    Get file record and content.
    """
    file = await get_file(db, file_id)
    
    if not os.path.exists(file.path):
        raise NotFoundError("File not found on disk")
    
    with open(file.path, "rb") as f:
        content = f.read()
    
    return file, content

async def delete_file(db: Session, file_id: int) -> None:
    """
    Delete file from disk and database.
    """
    file = await get_file(db, file_id)
    
    # Delete from disk
    if os.path.exists(file.path):
        os.remove(file.path)
    
    # Delete from database
    db.delete(file)
    db.commit()

async def get_file(db: Session, file_id: int) -> File:
    """
    Get file record by ID.
    """
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise NotFoundError("File not found")
    return file

async def get_user_files(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    file_type: Optional[FileType] = None
) -> List[File]:
    """
    Get all files for a user.
    """
    query = db.query(File).filter(File.user_id == user_id)
    
    if file_type:
        query = query.filter(File.file_type == file_type)
    
    return query.offset(skip).limit(limit).all()

async def save_uploaded_file(upload_file: UploadFile) -> str:
    """Saves an uploaded file to the storage directory and returns the file path."""
    try:
        file_path = os.path.join(STORAGE_DIR, upload_file.filename)
        # Ensure the filename is safe to prevent directory traversal issues
        # A more robust solution would generate a unique filename
        if not os.path.abspath(file_path).startswith(os.path.abspath(STORAGE_DIR)):
            # Handle invalid filename attempt
            return None # Or raise an exception

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return file_path
    finally:
        await upload_file.close()

def get_file_info(filename: str) -> dict | None:
    """Gets information about a stored file."""
    file_path = os.path.join(STORAGE_DIR, filename)
    if os.path.exists(file_path):
        return {
            "filename": filename,
            "size": os.path.getsize(file_path),
            "path": file_path
        }
    return None

def list_files() -> list[str]:
    """Lists all files in the storage directory."""
    return os.listdir(STORAGE_DIR) 