from typing import List
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
import io
import os

from config.database import get_db
from auth.dependencies import get_current_user
from .schemas import FileResponse, FileUpdate, FileUploadResponse, FileListResponse, FileInfo
from .services import (
    upload_file,
    download_file,
    delete_file,
    get_file,
    get_user_files,
    save_uploaded_file,
    get_file_info,
    list_files,
    STORAGE_DIR  # Import STORAGE_DIR directly from services
)
from .models import FileType

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file_route(file: UploadFile = FastAPIFile(...)):
    """Upload a file."""
    file_path = await save_uploaded_file(file)
    if file_path:
        file_info = get_file_info(file.filename)
        if file_info:
             # Construct the URL assuming the static directory is mounted at /static
            file_url = f"/static/uploads/{file.filename}"
            return FileUploadResponse(
                message="File uploaded successfully",
                file_info=FileInfo(
                    filename=file_info['filename'],
                    content_type=file.content_type,
                    size=file_info['size'],
                    url=file_url
                )
            )
        else:
             raise HTTPException(status_code=500, detail="Failed to get file info after upload")
    else:
        raise HTTPException(status_code=400, detail="Invalid filename or failed to save file")

@router.get("/list", response_model=FileListResponse)
def list_uploaded_files():
    """List all uploaded files."""
    filenames = list_files()
    files_info = []
    for filename in filenames:
        file_info = get_file_info(filename)
        if file_info:
             file_url = f"/static/uploads/{filename}"
             files_info.append(FileInfo(
                 filename=file_info['filename'],
                 content_type="unknown", # You might want to store content type during upload
                 size=file_info['size'],
                 url=file_url
             ))
    return FileListResponse(files=files_info)

@router.get("/uploads/{filename}", include_in_schema=False) # Serve files directly from static
async def read_uploaded_file(filename: str):
    """Serve a specific uploaded file."""
    file_path = os.path.join(STORAGE_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@router.get("/{file_id}")
async def read_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Download a file.
    """
    file, content = await download_file(db, file_id)
    
    # Check if user has access to the file
    if not file.is_public and file.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type=file.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file.original_filename}"'
        }
    )

@router.delete("/{file_id}")
async def remove_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a file.
    """
    file = await get_file(db, file_id)
    
    # Check if user owns the file
    if file.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this file")
    
    await delete_file(db, file_id)
    return {"message": "File deleted successfully"}

@router.get("", response_model=List[FileResponse])
async def list_files(
    skip: int = 0,
    limit: int = 100,
    file_type: FileType = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all files for the current user.
    """
    return await get_user_files(db, current_user["id"], skip, limit, file_type)

@router.patch("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    file_update: FileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update file metadata.
    """
    file = await get_file(db, file_id)
    
    # Check if user owns the file
    if file.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this file")
    
    for field, value in file_update.dict(exclude_unset=True).items():
        setattr(file, field, value)
    
    db.commit()
    db.refresh(file)
    return file 