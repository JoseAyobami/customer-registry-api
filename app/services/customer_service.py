from __future__ import annotations
import logging
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerSearchFilters, CustomerUpdate

logger = logging.getLogger(__name__)


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split()).casefold()



def to_customer_out(customer: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        business_name=customer.business_name,
        business_type=customer.business_type,
        industry=customer.industry,
        contact_email=customer.contact_email,
        contact_phone=customer.contact_phone,
        status=customer.status,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


def apply_filters(query, filters: CustomerSearchFilters):
    if filters.status:
        query = query.where(Customer.status == filters.status)
    if filters.business_type:
        query = query.where(Customer.business_type == filters.business_type)
    if filters.industry:
        query = query.where(Customer.industry.ilike(f"%{filters.industry.strip()}%"))
    if filters.q:
        term = f"%{filters.q.strip()}%"
        query = query.where(
            or_(
                Customer.business_name.ilike(term),
                Customer.business_type.ilike(term),
                Customer.industry.ilike(term),
                Customer.contact_email.ilike(term),
                Customer.contact_phone.ilike(term),
            )
        )
    return query


class CustomerService:
    """Service for customer registry operations."""

    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate) -> CustomerResponse:
        customer = Customer(
            id=str(uuid4()),
            business_name=customer_data.business_name.strip(),
            business_name_normalized=normalize_text(customer_data.business_name),
            business_type=customer_data.business_type,
            business_type_normalized=normalize_text(customer_data.business_type),
            industry=customer_data.industry.strip(),
            contact_email=str(customer_data.contact_email).strip().casefold(),
            contact_phone=customer_data.contact_phone.strip() if customer_data.contact_phone else None,
            status=customer_data.status,
            created_by="registry-api",
        )

        db.add(customer)
        try:
            db.commit()

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "A customer with the same business name, business type, or email already exists"
                )    
        

        db.refresh(customer)
        out = to_customer_out(customer)

        return out

    @staticmethod
    def get_customer(db: Session, customer_id: UUID | str) -> CustomerResponse | None:
        customer = db.get(Customer, str(customer_id))
        if customer is None:
            logger.warning("Customer not found: id=%s", customer_id)
            return None
        return to_customer_out(customer)
    
    

    @staticmethod
    def list_customers(
        db: Session,
        filters: CustomerSearchFilters | None = None,
        skip: int = 0,
        limit: int = 100,
        ) -> tuple[list[CustomerResponse], int]:
        filters = filters or CustomerSearchFilters()
        base_query = apply_filters(select(Customer), filters)
        count_query = apply_filters(
            select(func.count()).select_from(Customer),
            filters,
            )
        total = db.execute(count_query).scalar_one()
        
        customers = (
            db.execute(
                base_query
                .order_by(Customer.created_at.desc())
                .offset(skip)
                .limit(limit)
                )
                .scalars()
                .all()
                )
        return [to_customer_out(customer) for customer in customers], total
    
    
    @staticmethod
    def search_customers(
        db: Session,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[CustomerResponse], int]:
        filters = CustomerSearchFilters(q=search_term)
        return CustomerService.list_customers(db, filters, skip=skip, limit=limit)

    @staticmethod
    def update_customer(db: Session, customer_id: UUID | str, update_data: CustomerUpdate) -> CustomerResponse | None:
        customer = db.get(Customer, str(customer_id))
        if customer is None:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        if "business_name" in update_dict and update_dict["business_name"] is not None:
            customer.business_name = update_dict["business_name"].strip()
            customer.business_name_normalized = normalize_text(update_dict["business_name"])
        if "business_type" in update_dict and update_dict["business_type"] is not None:
            customer.business_type = update_dict["business_type"]
            customer.business_type_normalized = normalize_text(update_dict["business_type"])
        if "industry" in update_dict and update_dict["industry"] is not None:
            customer.industry = update_dict["industry"].strip()
        if "contact_email" in update_dict and update_dict["contact_email"] is not None:
            customer.contact_email = str(update_dict["contact_email"]).strip().casefold()
        if "contact_phone" in update_dict:
            customer.contact_phone = update_dict["contact_phone"].strip() if update_dict["contact_phone"] else None
        if "status" in update_dict and update_dict["status"] is not None:
            customer.status = update_dict["status"]

        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            
            raise ValueError(
                "A customer with the same business name, business type, or email already exists"
            )

        db.refresh(customer)
        return to_customer_out(customer)
    

    @staticmethod
    def get_customer_by_email(
        db: Session,
        email: str,
        ) -> CustomerResponse | None:
        
        customer = db.execute(
            select(Customer).where(
                Customer.contact_email == email.strip().casefold()
                )
                ).scalar_one_or_none()
        if customer is None:
            return None
        return to_customer_out(customer)
