from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    duration: int = Field(..., gt=0)  # Duration in minutes
    price: float = Field(..., gt=0)

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    duration: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)

class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 