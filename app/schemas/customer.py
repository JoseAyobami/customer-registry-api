from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

CustomerStatus = Literal["active", "inactive", "pending"]
CustomerType = Literal["corporation", "partnership", "llc", "sole_proprietorship", "non_profit", "other"]


class CustomerBase(BaseModel):
    
    business_name: str = Field(..., min_length=1, max_length=255, description="Legal business name")
    business_type: CustomerType = Field(..., description="Type: e.g., LLC, Corporation, Partnership")
    industry: str = Field(..., min_length=1, max_length=100, description="Industry classification")
    contact_email: EmailStr = Field(..., description="Primary contact email")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Optional contact phone number")
    status: CustomerStatus = Field("active", description="Customer status: active, inactive, pending")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: CustomerStatus) -> CustomerStatus:
        """Validate status is one of allowed values."""
        return v
    
    @field_validator("business_type", "industry")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Remove whitespace."""
        return v.strip() if v else v


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):    
    business_name: Optional[str] = Field(None, min_length=1, max_length=255)
    business_type: Optional[CustomerType] = Field(None)
    industry: Optional[str] = Field(None, min_length=1, max_length=100)
    contact_email: Optional[EmailStr] = Field(None)
    contact_phone: Optional[str] = Field(None, max_length=20)
    status: Optional[CustomerStatus] = Field(None)
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[CustomerStatus]) -> Optional[CustomerStatus]:
        """Validate status if provided."""
        return v


class CustomerResponse(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    total: int
    count: int
    items: list[CustomerResponse]

class CustomerSearchFilters(BaseModel):    
    q: Optional[str] = Field(None, description="Search term for business name or email")
    status: Optional[CustomerStatus] = Field(None, description="Filter by status")
    business_type: Optional[CustomerType] = Field(None, description="Filter by business type")
    industry: Optional[str] = Field(None, description='Filter by industry')

    


class ErrorResponse(BaseModel):    
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Detailed error message")
    details: Optional[dict] = Field(None, description="Additional error context")
