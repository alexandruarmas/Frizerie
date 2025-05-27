from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from auth.dependencies import get_current_admin
from users.models import User
from . import services
from .schemas import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/services", tags=["services"])

@router.post("", response_model=ServiceResponse)
async def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Create a new service.
    Only accessible by admin users.
    """
    return await services.create_service(db, service_data)

@router.get("", response_model=List[ServiceResponse])
async def get_services(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all services.
    """
    return await services.get_services(db, skip=skip, limit=limit)

@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific service by ID.
    """
    service = await services.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Update a service.
    Only accessible by admin users.
    """
    service = await services.update_service(db, service_id, service_data)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Delete a service.
    Only accessible by admin users.
    """
    success = await services.delete_service(db, service_id)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"} 