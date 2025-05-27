from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from .models import Service, ServiceCategory
from .schemas import ServiceCreate, ServiceUpdate

async def create_service(
    db: Session,
    name: str,
    description: Optional[str],
    price: float,
    duration_minutes: int,
    category_id: Optional[int] = None
) -> Service:
    """
    Create a new service.
    """
    # Check if category exists if category_id is provided
    if category_id:
        category = get_service_category_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found")

    service = Service(
        name=name,
        description=description,
        price=price,
        duration_minutes=duration_minutes,
        category_id=category_id
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

async def get_services(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None
) -> List[Service]:
    """
    Get all services with pagination.
    """
    query = db.query(Service).filter(Service.is_active == True)
    if category_id is not None:
        query = query.filter(Service.category_id == category_id)
    return query.offset(skip).limit(limit).all()

async def get_service(
    db: Session,
    service_id: int
) -> Optional[Service]:
    """
    Get a service by ID.
    """
    return db.query(Service).filter(Service.id == service_id, Service.is_active == True).first()

async def update_service(
    db: Session,
    service_id: int,
    service_data: Dict[str, Any]
) -> Service:
    """
    Update a service.
    """
    service = await get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    
    # Check if category exists if category_id is updated
    if "category_id" in service_data and service_data["category_id"] is not None:
        category = get_service_category_by_id(db, service_data["category_id"])
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found")

    for key, value in service_data.items():
        setattr(service, key, value)
    
    db.commit()
    db.refresh(service)
    return service

async def delete_service(
    db: Session,
    service_id: int
) -> bool:
    """
    Delete a service.
    """
    service = await get_service(db, service_id)
    if not service:
        return False
    
    service.is_active = False # Soft delete
    db.commit()
    db.refresh(service)
    return True

# Service Category Service Functions
async def create_service_category(
    db: Session,
    name: str,
    description: Optional[str] = None
) -> ServiceCategory:
    """
    Create a new service category.
    """
    # Check if category name already exists
    existing_category = get_service_category_by_name(db, name)
    if existing_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Service category with this name already exists")

    category = ServiceCategory(
        name=name,
        description=description
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

async def get_service_category_by_id(db: Session, category_id: int) -> Optional[ServiceCategory]:
    """
    Get a service category by ID.
    """
    return db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()

async def get_service_category_by_name(db: Session, name: str) -> Optional[ServiceCategory]:
    """
    Get a service category by name.
    """
    return db.query(ServiceCategory).filter(ServiceCategory.name == name).first()

async def get_all_service_categories(db: Session, skip: int = 0, limit: int = 10) -> List[ServiceCategory]:
    """
    Get all service categories.
    """
    return db.query(ServiceCategory).offset(skip).limit(limit).all()

async def update_service_category(
    db: Session,
    category_id: int,
    category_data: Dict[str, Any]
) -> ServiceCategory:
    """
    Update a service category.
    """
    category = get_service_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found")

    for key, value in category_data.items():
        if key == "name" and get_service_category_by_name(db, value) and get_service_category_by_name(db, value).id != category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Service category with this name already exists")
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category

async def delete_service_category(db: Session, category_id: int) -> ServiceCategory:
    """
    Delete a service category and remove its association from services.
    """
    category = get_service_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found")

    # Remove category association from services
    services_in_category = db.query(Service).filter(Service.category_id == category_id).all()
    for service in services_in_category:
        service.category_id = None # Or set to a default category, if one exists

    db.delete(category)
    db.commit()
    return category

# New admin service functions for service management
async def admin_get_all_services(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None
) -> List[Service]:
    """Admin function to get a list of all services (including inactive), optionally filtered by category."""
    query = db.query(Service)
    if category_id is not None:
        query = query.filter(Service.category_id == category_id)
    return query.offset(skip).limit(limit).all()

async def admin_get_service(db: Session, service_id: int) -> Optional[Service]:
    """Admin function to get a single service by ID (including inactive)."""
    return db.query(Service).filter(Service.id == service_id).first()

async def admin_create_service(
    db: Session,
    service_data: ServiceCreate
) -> Service:
    """Admin function to create a new service."""
     # Check if category exists if category_id is provided
    if service_data.category_id:
        category = get_service_category_by_id(db, service_data.category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found")

    service = Service(
        name=service_data.name,
        description=service_data.description,
        price=service_data.price,
        duration_minutes=service_data.duration_minutes,
        category_id=service_data.category_id,
        is_active=True # Admins can create active services
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

async def admin_update_service(
    db: Session,
    service_id: int,
    service_data: Dict[str, Any]
) -> Service:
    """Admin function to update an existing service."""
    service = admin_get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    # Check if category exists if category_id is updated
    if "category_id" in service_data and service_data["category_id"] is not None:
        category = get_service_category_by_id(db, service_data["category_id"])
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found")

    for key, value in service_data.items():
         if hasattr(service, key) and key != "id":
            setattr(service, key, value)

    db.commit()
    db.refresh(service)
    return service

async def admin_hard_delete_service(db: Session, service_id: int) -> Dict[str, bool]:
    """Admin function to permanently delete a service."""
    service = admin_get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    db.delete(service)
    db.commit()
    return {"success": True}

async def admin_set_service_active_status(db: Session, service_id: int, is_active: bool) -> Service:
    """Admin function to activate or deactivate a service."""
    service = admin_get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    service.is_active = is_active
    db.commit()
    db.refresh(service)
    return service 