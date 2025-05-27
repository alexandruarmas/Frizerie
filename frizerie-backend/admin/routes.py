from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from config.database import get_db
from auth.dependencies import get_current_admin
from users import services as user_services
from users.models import User, Role, Permission, AuditLog # Import User model for dependency type hint
from validation import UserCreate, UserUpdate, UserResponse # Import user schemas

from stylists import services as stylist_services
from validation import StylistCreate, StylistBase, StylistResponse # Import stylist schemas

from services import services as service_services
from validation.schemas import ServiceCreate, ServiceCategoryCreate, ServiceCategoryUpdate, ServiceCategoryResponse # Import service schemas directly from schemas.py
from services.models import Service # Import Service model for dependency type hint

from validation.schemas import (
    RoleCreate, RoleUpdate, RoleResponse,
    PermissionCreate, PermissionUpdate, PermissionResponse,
    UserRoleUpdate,
    AuditLogResponse
)

router = APIRouter(prefix="/admin", tags=["Admin"])

# Admin User Management Routes
@router.get("/users", response_model=List[UserResponse])
async def admin_get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin) # Ensure admin access
):
    """Admin: Get all users."""
    users = user_services.get_all_users(db, skip=skip, limit=limit)
    return users

@router.post("/users", response_model=UserResponse)
async def admin_create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin) # Ensure admin access
):
    """Admin: Create a new user."""
    user = user_services.admin_create_user(db, user_data)
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin) # Ensure admin access
):
    """Admin: Update a user."""
    user = user_services.admin_update_user(db, user_id, user_data)
    return user

@router.delete("/users/{user_id}", response_model=Dict[str, bool])
async def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin) # Ensure admin access
):
    """Admin: Delete a user."""
    result = user_services.admin_delete_user(db, user_id)
    return result

# Admin Stylist Management Routes
@router.get("/stylists", response_model=List[StylistResponse])
async def admin_get_all_stylists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Get all stylists (including inactive)."""
    return stylist_services.admin_get_all_stylists(db, skip=skip, limit=limit)

@router.get("/stylists/{stylist_id}", response_model=StylistResponse)
async def admin_get_stylist(
    stylist_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Get a single stylist by ID (including inactive)."""
    stylist = stylist_services.admin_get_stylist_by_id(db, stylist_id)
    if not stylist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found")
    return stylist

@router.post("/stylists", response_model=StylistResponse)
async def admin_create_stylist(
    stylist_data: StylistCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Create a new stylist."""
    return stylist_services.admin_create_stylist(db, stylist_data)

@router.put("/stylists/{stylist_id}", response_model=StylistResponse)
async def admin_update_stylist(
    stylist_id: int,
    stylist_data: Dict[str, Any],
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Update a stylist."""
    return stylist_services.admin_update_stylist(db, stylist_id, stylist_data)

@router.delete("/stylists/{stylist_id}", response_model=Dict[str, bool])
async def admin_delete_stylist(
    stylist_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Delete a stylist (hard delete)."""
    return stylist_services.admin_delete_stylist(db, stylist_id)

@router.patch("/stylists/{stylist_id}/status", response_model=StylistResponse)
async def admin_set_stylist_active_status(
    stylist_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Activate or deactivate a stylist."""
    return stylist_services.admin_set_stylist_active_status(db, stylist_id, is_active)

# Admin Service Management Routes
@router.get("/services", response_model=List[Dict[str, Any]]) # Using Dict for now to include category name
async def admin_get_all_services(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Get all services (including inactive), optionally filtered by category."""
    services = service_services.admin_get_all_services(db, skip=skip, limit=limit, category_id=category_id)
    # Manually add category name for now, ideally adjust schema if needed
    return [{"category_name": service.category.name if service.category else None, **service.__dict__} for service in services]

@router.get("/services/{service_id}", response_model=Dict[str, Any]) # Using Dict for now to include category name
async def admin_get_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Get a single service by ID (including inactive)."""
    service = service_services.admin_get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return {"category_name": service.category.name if service.category else None, **service.__dict__}

@router.post("/services", response_model=Dict[str, Any]) # Using Dict for now
async def admin_create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Create a new service."""
    service = service_services.admin_create_service(db, service_data)
    return {"category_name": service.category.name if service.category else None, **service.__dict__}

@router.put("/services/{service_id}", response_model=Dict[str, Any]) # Using Dict for now
async def admin_update_service(
    service_id: int,
    service_data: Dict[str, Any],
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Update a service."""
    service = service_services.admin_update_service(db, service_id, service_data)
    return {"category_name": service.category.name if service.category else None, **service.__dict__}

@router.delete("/services/{service_id}", response_model=Dict[str, bool])
async def admin_hard_delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Permanently delete a service."""
    return service_services.admin_hard_delete_service(db, service_id)

@router.patch("/services/{service_id}/status", response_model=Dict[str, Any]) # Using Dict for now
async def admin_set_service_active_status(
    service_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Activate or deactivate a service."""
    service = service_services.admin_set_service_active_status(db, service_id, is_active)
    return {"category_name": service.category.name if service.category else None, **service.__dict__}

# Admin Service Category Management Routes
@router.get("/service-categories", response_model=List[ServiceCategoryResponse])
async def admin_get_all_service_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Get all service categories."""
    return service_services.get_all_service_categories(db, skip=skip, limit=limit)

@router.get("/service-categories/{category_id}", response_model=ServiceCategoryResponse)
async def admin_get_service_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Get a single service category by ID."""
    category = service_services.get_service_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found")
    return category

@router.post("/service-categories", response_model=ServiceCategoryResponse)
async def admin_create_service_category(
    category_data: ServiceCategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Create a new service category."""
    return service_services.create_service_category(db, category_data.name, category_data.description)

@router.put("/service-categories/{category_id}", response_model=ServiceCategoryResponse)
async def admin_update_service_category(
    category_id: int,
    category_data: Dict[str, Any],
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Update a service category."""
    return service_services.update_service_category(db, category_id, category_data)

@router.delete("/service-categories/{category_id}", response_model=Dict[str, bool])
async def admin_delete_service_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin: Delete a service category."""
    category = service_services.delete_service_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found")
    return {"success": True}

# Role Management Routes
@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    request: Request = None
):
    """Create a new role."""
    try:
        role = user_services.create_role(db, role_data)
        user_services.log_admin_action(
            db,
            admin_user.id,
            "create",
            "role",
            role.id,
            {"role_name": role.name},
            request
        )
        return role
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role"
        )

@router.get("/roles", response_model=List[RoleResponse])
async def get_all_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get all roles."""
    return user_services.get_all_roles(db, skip=skip, limit=limit)

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get a role by ID."""
    role = user_services.get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    request: Request = None
):
    """Update a role."""
    try:
        role = user_services.update_role(db, role_id, role_data)
        user_services.log_admin_action(
            db,
            admin_user.id,
            "update",
            "role",
            role.id,
            {"role_name": role.name},
            request
        )
        return role
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role"
        )

@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    request: Request = None
):
    """Delete a role."""
    try:
        role = user_services.get_role(db, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        success = user_services.delete_role(db, role_id)
        if success:
            user_services.log_admin_action(
                db,
                admin_user.id,
                "delete",
                "role",
                role_id,
                {"role_name": role.name},
                request
            )
        return {"success": success}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role"
        )

# Permission Management Routes
@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    request: Request = None
):
    """Create a new permission."""
    try:
        permission = user_services.create_permission(db, permission_data)
        user_services.log_admin_action(
            db,
            admin_user.id,
            "create",
            "permission",
            permission.id,
            {"permission_name": permission.name},
            request
        )
        return permission
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create permission"
        )

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_all_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get all permissions."""
    return user_services.get_all_permissions(db, skip=skip, limit=limit)

@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get a permission by ID."""
    permission = user_services.get_permission(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission

@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    request: Request = None
):
    """Update a permission."""
    try:
        permission = user_services.update_permission(db, permission_id, permission_data)
        user_services.log_admin_action(
            db,
            admin_user.id,
            "update",
            "permission",
            permission.id,
            {"permission_name": permission.name},
            request
        )
        return permission
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update permission"
        )

@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    request: Request = None
):
    """Delete a permission."""
    try:
        permission = user_services.get_permission(db, permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        success = user_services.delete_permission(db, permission_id)
        if success:
            user_services.log_admin_action(
                db,
                admin_user.id,
                "delete",
                "permission",
                permission_id,
                {"permission_name": permission.name},
                request
            )
        return {"success": success}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete permission"
        )

# User Role Management Routes
@router.put("/users/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    request: Request = None
):
    """Update a user's roles."""
    try:
        user = user_services.update_user_roles(db, user_id, role_data)
        user_services.log_admin_action(
            db,
            admin_user.id,
            "update_roles",
            "user",
            user_id,
            {"roles": [role.name for role in user.roles]},
            request
        )
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user roles"
        )

# Audit Log Routes
@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get audit logs with optional filtering."""
    return user_services.get_audit_logs(
        db,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    ) 