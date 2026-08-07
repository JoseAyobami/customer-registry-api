import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.customer import (
    CustomerStatus,
    CustomerType,
    CustomerCreate,
    CustomerResponse,
    CustomerSearchFilters,
    CustomerUpdate,
    CustomerListResponse,
    ErrorResponse,
)
from app.services.customer_service import CustomerService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Customer successfully created"},
        400: {"model": ErrorResponse, "description": "Invalid input or duplicate email"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def register_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
):
    try:
        db_customer = CustomerService.create_customer(db, customer)
        return db_customer
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error on customer creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DUPLICATE_EMAIL",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.exception(f"Error creating customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to create customer"},
        )


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={
        200: {"description": "Customer found"},
        404: {"model": ErrorResponse, "description": "Customer not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    customer = CustomerService.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": f"Customer with id {customer_id} not found",
            },
        )
    return customer


@router.get(
    "",
    response_model=CustomerListResponse,
    responses={
        200: {"description": "Customers retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def list_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    q: Optional[str] = Query(None, min_length=1, max_length=255, description="Search term"),
    business_type: Optional[CustomerType] = Query(None, description="Filter by business type"),
    industry: Optional[str] = Query(None, min_length=1, max_length=120, description="Filter by industry"),
    status_filter: Optional[CustomerStatus] = Query(None, alias="status", description="Filter by status (active/inactive/pending)"),
    db: Session = Depends(get_db),
):
    try:
        filters = CustomerSearchFilters(q=q, business_type=business_type, industry=industry, status=status_filter)
        customers, total = CustomerService.list_customers(db, filters, skip, limit)
        return CustomerListResponse(
            total=total,
            count=len(customers),
            items=customers,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error listing customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to list customers"},
        )


@router.get(
    "/search/query",
    response_model=CustomerListResponse,
    responses={
        200: {"description": "Search completed"},
        400: {"model": ErrorResponse, "description": "Invalid search parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def search_customers(
    q: str = Query(..., min_length=1, max_length=255, description="Search term"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: Session = Depends(get_db),
):
    
    try:
        customers, total = CustomerService.search_customers(db, q, skip, limit)
        return CustomerListResponse(
            total=total,
            count=len(customers),
            items=customers,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error searching customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to search customers"},
        )


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={
        200: {"description": "Customer updated"},
        404: {"model": ErrorResponse, "description": "Customer not found"},
        400: {"model": ErrorResponse, "description": "Invalid update (e.g., duplicate email)"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def update_customer(
    customer_id: UUID,
    update_data: CustomerUpdate,
    db: Session = Depends(get_db),
):
    
    try:
        customer = CustomerService.update_customer(db, customer_id, update_data)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NOT_FOUND",
                    "message": f"Customer with id {customer_id} not found",
                },
            )
        return customer
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error on customer update: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_UPDATE",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.exception(f"Error updating customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to update customer"},
        )


# idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
# idempotency_key=idempotency_key