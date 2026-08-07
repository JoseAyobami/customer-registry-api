import pytest
from sqlalchemy.orm import Session

from app.schemas.customer import CustomerCreate
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerSearchFilters, CustomerUpdate


class TestCustomerServiceCreate:

    def test_create_customer_success(self, db: Session, sample_customer_data):

        customer = CustomerService.create_customer(
            db,
            CustomerCreate(**sample_customer_data),
        )

        assert customer.id is not None
        assert customer.business_name == sample_customer_data["business_name"]
        assert customer.contact_email == sample_customer_data["contact_email"]
        assert customer.status == "active"

    def test_create_customer_duplicate_email_raises_error(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Duplicate email should not be allowed."""

        CustomerService.create_customer(
            db,
            CustomerCreate(**sample_customer_data),
        )

        duplicate = sample_customer_data.copy()
        duplicate["business_name"] = "Another Company"

        with pytest.raises(ValueError) as exc:
            CustomerService.create_customer(
                db,
                CustomerCreate(**duplicate),
            )

        assert "already exists" in str(exc.value)

    def test_create_customer_duplicate_business_raises_error(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Duplicate business name/type should not be allowed."""

        CustomerService.create_customer(
            db,
            CustomerCreate(**sample_customer_data),
        )

        duplicate = sample_customer_data.copy()
        duplicate["contact_email"] = "different@example.com"

        with pytest.raises(ValueError) as exc:
            CustomerService.create_customer(
                db,
                CustomerCreate(**duplicate),
            )

        assert "already exists" in str(exc.value)

    def test_create_customer_defaults_to_active_status(
        self,
        db: Session,
        sample_customer_minimal,
    ):
        """Status defaults to active."""

        customer = CustomerService.create_customer(
            db,
            CustomerCreate(**sample_customer_minimal),
        )

        assert customer.status == "active"


class TestCustomerServiceGet:
    """Tests for CustomerService.get_customer()."""

    def test_get_customer_by_id(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Retrieve an existing customer."""

        created = CustomerService.create_customer(
            db,
            CustomerCreate(**sample_customer_data),
        )

        customer = CustomerService.get_customer(db, created.id)

        assert customer is not None
        assert customer.id == created.id
        assert customer.business_name == created.business_name
        assert customer.contact_email == created.contact_email

    def test_get_customer_not_found_returns_none(self, db: Session):

        customer = CustomerService.get_customer(
            db,
            "00000000-0000-0000-0000-000000000000",
        )

        assert customer is None



class TestCustomerServiceList:
    """Tests for CustomerService.list_customers()."""

    def test_list_empty_database(self, db: Session):
        """Listing an empty database returns no customers."""

        customers, total = CustomerService.list_customers(
            db,
            CustomerSearchFilters(),
        )

        assert total == 0
        assert customers == []

    def test_list_all_customers(
        self,
        db: Session,
        sample_customer_data,
    ):
        """List all customers."""

        for i in range(3):
            data = sample_customer_data.copy()
            data["business_name"] = f"Company {i}"
            data["contact_email"] = f"company{i}@example.com"

            CustomerService.create_customer(
                db,
                CustomerCreate(**data),
            )

        customers, total = CustomerService.list_customers(
            db,
            CustomerSearchFilters(),
        )

        assert total == 3
        assert len(customers) == 3

    def test_list_with_pagination(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Pagination returns the expected number of records."""

        for i in range(5):
            data = sample_customer_data.copy()
            data["business_name"] = f"Page Company {i}"
            data["contact_email"] = f"page{i}@example.com"

            CustomerService.create_customer(
                db,
                CustomerCreate(**data),
            )

        customers, total = CustomerService.list_customers(
            db,
            CustomerSearchFilters(),
            skip=0,
            limit=2,
        )

        assert total == 5
        assert len(customers) == 2

        customers, _ = CustomerService.list_customers(
            db,
            CustomerSearchFilters(),
            skip=2,
            limit=2,
        )

        assert len(customers) == 2

        customers, _ = CustomerService.list_customers(
            db,
            CustomerSearchFilters(),
            skip=4,
            limit=2,
        )

        assert len(customers) == 1

    def test_filter_by_status(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Filter customers by status."""

        active = sample_customer_data.copy()
        active["business_name"] = "Active Company"
        active["contact_email"] = "active@example.com"
        active["status"] = "active"

        inactive = sample_customer_data.copy()
        inactive["business_name"] = "Inactive Company"
        inactive["contact_email"] = "inactive@example.com"
        inactive["status"] = "inactive"

        CustomerService.create_customer(
            db,
            CustomerCreate(**active),
        )

        CustomerService.create_customer(
            db,
            CustomerCreate(**inactive),
        )

        customers, total = CustomerService.list_customers(
            db,
            CustomerSearchFilters(status="active"),
        )

        assert total == 1
        assert customers[0].status == "active"


class TestCustomerServiceSearch:
    """Tests for CustomerService.search_customers()."""

    def test_search_by_business_name(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Search customers by business name."""

        data = sample_customer_data.copy()
        data["business_name"] = "Tech Solutions Limited"
        data["contact_email"] = "tech@example.com"

        CustomerService.create_customer(
            db,
            CustomerCreate(**data),
        )

        customers, total = CustomerService.search_customers(
            db,
            "Tech",
        )

        assert total == 1
        assert customers[0].business_name == "Tech Solutions Limited"

    def test_search_no_results(self, db: Session):
        """Searching for a missing customer returns nothing."""

        customers, total = CustomerService.search_customers(
            db,
            "DoesNotExist",
        )

        assert total == 0
        assert customers == []

    def test_search_with_pagination(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Search supports pagination."""

        for i in range(5):
            data = sample_customer_data.copy()
            data["business_name"] = f"Search Company {i}"
            data["contact_email"] = f"search{i}@example.com"

            CustomerService.create_customer(
                db,
                CustomerCreate(**data),
            )

        customers, total = CustomerService.search_customers(
            db,
            "Search",
            skip=0,
            limit=2,
        )

        assert total == 5
        assert len(customers) == 2

class TestCustomerServiceUpdate:
    """Tests for CustomerService.update_customer()."""

    def test_update_customer_success(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Update an existing customer."""

        customer = CustomerService.create_customer(
            db,
            CustomerCreate(**sample_customer_data),
        )

        update_data = CustomerUpdate(
            status="inactive",
            contact_phone="555-9999",
        )

        updated = CustomerService.update_customer(
            db,
            customer.id,
            update_data,
        )

        assert updated is not None
        assert updated.status == "inactive"
        assert updated.contact_phone == "555-9999"
        assert updated.business_name == customer.business_name

    def test_update_customer_not_found_returns_none(
        self,
        db: Session,
    ):
        """Updating a missing customer returns None."""

        result = CustomerService.update_customer(
            db,
            "00000000-0000-0000-0000-000000000000",
            CustomerUpdate(status="inactive"),
        )

        assert result is None

    def test_update_duplicate_email_raises_error(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Updating to an existing email should fail."""

        customer1 = sample_customer_data.copy()
        customer1["business_name"] = "First Company"
        customer1["contact_email"] = "first@test.com"

        customer2 = sample_customer_data.copy()
        customer2["business_name"] = "Second Company"
        customer2["contact_email"] = "second@test.com"

        first = CustomerService.create_customer(
            db,
            CustomerCreate(**customer1),
        )

        second = CustomerService.create_customer(
            db,
            CustomerCreate(**customer2),
        )

        with pytest.raises(ValueError) as exc:
            CustomerService.update_customer(
                db,
                second.id,
                CustomerUpdate(contact_email=first.contact_email),
            )

        assert "already exists" in str(exc.value)

    def test_update_same_email_is_allowed(
        self,
        db: Session,
        sample_customer_data,
    ):
        """Updating a customer with its current email should succeed."""

        customer = CustomerService.create_customer(
            db,
            CustomerCreate(**sample_customer_data),
        )

        updated = CustomerService.update_customer(
            db,
            customer.id,
            CustomerUpdate(contact_email=customer.contact_email),
        )

        assert updated is not None
        assert updated.contact_email == customer.contact_email




























































# """Unit tests for customer service business logic."""

# import pytest
# from sqlalchemy.orm import Session
# from app.models.customer import Customer
# from app.schemas.customer import CustomerCreate, CustomerUpdate
# from app.services.customer_service import CustomerService


# class TestCustomerServiceCreate:
#     """Tests for CustomerService.create_customer()."""
    
#     def test_create_customer_success(self, db: Session, sample_customer_data):
#         """Test successful customer creation."""
#         customer_create = CustomerCreate(**sample_customer_data)
#         customer = CustomerService.create_customer(db, customer_create)
        
#         assert customer.id is not None
#         assert customer.business_name == sample_customer_data["business_name"]
#         assert customer.contact_email == sample_customer_data["contact_email"]
#         assert customer.status == "active"
    
#     def test_create_customer_duplicate_email_raises_error(self, db: Session, sample_customer_data):
#         """Test that creating with duplicate email raises ValueError."""
#         customer_create = CustomerCreate(**sample_customer_data)
#         CustomerService.create_customer(db, customer_create)
        
#         # Attempt to create another with same email
#         with pytest.raises(ValueError) as exc_info:
#             CustomerService.create_customer(db, customer_create)
        
#         assert "already exists" in str(exc_info.value)
    
#     def test_create_customer_defaults_to_active_status(self, db: Session, sample_customer_minimal):
#         """Test that status defaults to 'active' when not provided."""
#         customer_create = CustomerCreate(**sample_customer_minimal)
#         customer = CustomerService.create_customer(db, customer_create)
        
#         assert customer.status == "active"
    
#     def test_create_customer_persists_to_database(self, db: Session, sample_customer_data):
#         """Test that created customer is retrievable from database."""
#         customer_create = CustomerCreate(**sample_customer_data)
#         created = CustomerService.create_customer(db, customer_create)
        
#         # Query directly
#         retrieved = db.query(Customer).filter(Customer.id == created.id).first()
#         assert retrieved is not None
#         assert retrieved.contact_email == created.contact_email


# class TestCustomerServiceGet:
#     """Tests for CustomerService.get_customer()."""
    
#     def test_get_customer_by_id(self, db: Session, sample_customer_data):
#         """Test retrieving a customer by ID."""
#         customer_create = CustomerCreate(**sample_customer_data)
#         created = CustomerService.create_customer(db, customer_create)
        
#         retrieved = CustomerService.get_customer(db, created.id)
        
#         assert retrieved is not None
#         assert retrieved.id == created.id
#         assert retrieved.business_name == created.business_name
    
#     def test_get_customer_not_found_returns_none(self, db: Session):
#         """Test that getting non-existent customer returns None."""
#         result = CustomerService.get_customer(db, 99999)
#         assert result is None


# class TestCustomerServiceList:
#     """Tests for CustomerService.list_customers()."""
    
#     def test_list_empty_database(self, db: Session):
#         """Test listing when no customers exist."""
#         customers, total = CustomerService.list_customers(db)
        
#         assert total == 0
#         assert customers == []
    
#     def test_list_all_customers(self, db: Session, sample_customer_data):
#         """Test listing all customers."""
#         # Create 3 customers
#         for i in range(3):
#             data = sample_customer_data.copy()
#             data["business_name"] = f"Company {i}"
#             data["contact_email"] = f"cust{i}@test.com"


#         # for i in range(3):
#         #     data = sample_customer_data.copy()
#         #     data["contact_email"] = f"cust{i}@test.com"
#             create_obj = CustomerCreate(**data)
#             CustomerService.create_customer(db, create_obj)
        
#         customers, total = CustomerService.list_customers(db)
        
#         assert total == 3
#         assert len(customers) == 3
    
#     def test_list_with_pagination(self, db: Session, sample_customer_data):
#         """Test pagination with skip and limit."""
#         for i in range(5):
#             data = sample_customer_data.copy()
#             data["business_name"] = f"Page Company {i}"
#             data["contact_email"] = f"page{i}@test.com"
#             create_obj = CustomerCreate(**data)
#             CustomerService.create_customer(db, create_obj)
        
#         # Get first 2
#         customers, total = CustomerService.list_customers(db, skip=0, limit=2)
#         assert len(customers) == 2
#         assert total == 5
        
#         # Get next 2
#         customers, total = CustomerService.list_customers(db, skip=2, limit=2)
#         assert len(customers) == 2
        
#         # Get remaining
#         customers, total = CustomerService.list_customers(db, skip=4, limit=2)
#         assert len(customers) == 1
    
#     def test_list_filter_by_status(self, db: Session, sample_customer_data):
#         """Test filtering by status."""
#         # Create active customer
#         active_data = sample_customer_data.copy()
#         active_data["business_name"] = "Active Company"
#         active_data["status"] = "active"
#         active_data["contact_email"] = "active@test.com"
#         CustomerService.create_customer(db, CustomerCreate(**active_data))
        
#         # Create inactive customer
#         inactive_data = sample_customer_data.copy()
#         inactive_data["business_name"] = "Inactive Company"
#         inactive_data["status"] = "inactive"
#         inactive_data["contact_email"] = "inactive@test.com"
#         CustomerService.create_customer(db, CustomerCreate(**inactive_data))
        
#         # Filter for active
#         active_customers, total = CustomerService.list_customers(db, status="active")
#         assert len(active_customers) == 1
#         assert active_customers[0].status == "active"
#         assert total == 1
        
#         # Filter for inactive
#         inactive_customers, total = CustomerService.list_customers(db, status="inactive")
#         assert len(inactive_customers) == 1
#         assert total == 1


# class TestCustomerServiceSearch:
#     """Tests for CustomerService.search_customers()."""
    
#     def test_search_by_business_name(self, db: Session, sample_customer_data):
#         """Test searching by business name."""
#         sample_customer_data["business_name"] = "Tech Solutions Inc"
#         sample_customer_data["contact_email"] = "tech@test.com"
#         CustomerService.create_customer(db, CustomerCreate(**sample_customer_data))
        
#         results, total = CustomerService.search_customers(db, "Tech")
#         assert total == 1
#         assert results[0].business_name == "Tech Solutions Inc"
    
#     def test_search_by_email(self, db: Session, sample_customer_data):
#         """Test searching by email."""
#         sample_customer_data["contact_email"] = "unique@domain.io"
#         CustomerService.create_customer(db, CustomerCreate(**sample_customer_data))
        
#         results, total = CustomerService.search_customers(db, "unique@domain")
#         assert total == 1
    
#     def test_search_by_phone(self, db: Session, sample_customer_data):
#         """Test searching by phone."""
#         sample_customer_data["contact_phone"] = "555-1234"
#         sample_customer_data["contact_email"] = "phone@test.com"
#         CustomerService.create_customer(db, CustomerCreate(**sample_customer_data))
        
#         results, total = CustomerService.search_customers(db, "555-1234")
#         assert total == 1
    
#     def test_search_case_insensitive(self, db: Session, sample_customer_data):
#         """Test that search is case-insensitive."""
#         sample_customer_data["business_name"] = "CaseSensitive Corp"
#         sample_customer_data["contact_email"] = "case@test.com"
#         CustomerService.create_customer(db, CustomerCreate(**sample_customer_data))
        
#         results_lower, _ = CustomerService.search_customers(db, "casesensitive")
#         results_upper, _ = CustomerService.search_customers(db, "CASESENSITIVE")
        
#         assert len(results_lower) == 1
#         assert len(results_upper) == 1
    
#     def test_search_no_results(self, db: Session):
#         """Test search with no matching results."""
#         results, total = CustomerService.search_customers(db, "nonexistent")
#         assert total == 0
#         assert results == []
    
#     def test_search_with_pagination(self, db: Session, sample_customer_data):
#         """Test search with pagination."""
#         for i in range(5):
#             data = sample_customer_data.copy()
#             data["business_name"] = f"Search Company {i}"
#             data["contact_email"] = f"search{i}@test.com"
#             CustomerService.create_customer(db, CustomerCreate(**data))
        
#         results, total = CustomerService.search_customers(db, "Search", skip=0, limit=2)
#         assert len(results) == 2
#         assert total == 5


# class TestCustomerServiceUpdate:
#     """Tests for CustomerService.update_customer()."""
    
#     def test_update_single_field(self, db: Session, sample_customer_data):
#         """Test updating a single field."""
#         customer = CustomerService.create_customer(db, CustomerCreate(**sample_customer_data))
        
#         update_data = CustomerUpdate(status="inactive")
#         updated = CustomerService.update_customer(db, customer.id, update_data)
        
#         assert updated.status == "inactive"
#         assert updated.business_name == customer.business_name
    
#     def test_update_multiple_fields(self, db: Session, sample_customer_data):
#         """Test updating multiple fields."""
#         customer = CustomerService.create_customer(db, CustomerCreate(**sample_customer_data))
        
#         update_data = CustomerUpdate(
#             business_type="partnership",
#             status="pending",
#             contact_phone="555-9999",
#         )
#         updated = CustomerService.update_customer(db, customer.id, update_data)
        
#         assert updated.business_type == "partnership"
#         assert updated.status == "pending"
#         assert updated.contact_phone == "555-9999"
    
#     def test_update_nonexistent_customer_returns_none(self, db: Session):
#         """Test updating non-existent customer returns None."""
#         update_data = CustomerUpdate(status="inactive")
#         result = CustomerService.update_customer(db, 99999, update_data)
        
#         assert result is None
    
#     def test_update_to_duplicate_email_raises_error(self, db: Session, sample_customer_data):
#         """Test that updating to existing email raises ValueError."""
#         # Create two customers
#         cust1_data = sample_customer_data.copy()
#         cust1_data["business_name"] = "First Company"
#         cust1_data["contact_email"] = "first@test.com"
#         cust1 = CustomerService.create_customer(db, CustomerCreate(**cust1_data))
        
#         cust2_data = sample_customer_data.copy()
#         cust2_data["business_name"] = "Second Company"
#         cust2_data["contact_email"] = "second@test.com"
#         cust2 = CustomerService.create_customer(db, CustomerCreate(**cust2_data))
        
#         # Try to update cust2 with cust1's email
#         update_data = CustomerUpdate(contact_email="first@test.com")
#         with pytest.raises(ValueError) as exc_info:
#             CustomerService.update_customer(db, cust2.id, update_data)
        
#         assert "already in use" in str(exc_info.value)
    
#     def test_update_own_email_allowed(self, db: Session, sample_customer_data):
#         """Test that updating to same email is allowed."""
#         customer = CustomerService.create_customer(db, CustomerCreate(**sample_customer_data))
        
#         update_data = CustomerUpdate(contact_email=customer.contact_email)
#         updated = CustomerService.update_customer(db, customer.id, update_data)
        
#         assert updated is not None
#         assert updated.contact_email == customer.contact_email


# class TestCustomerServiceGetByEmail:
#     """Tests for CustomerService.get_customer_by_email()."""
    
#     def test_get_customer_by_email(self, db: Session, sample_customer_data):
#         """Test retrieving customer by email."""
#         CustomerService.create_customer(db, CustomerCreate(**sample_customer_data))
        
#         customer = CustomerService.get_customer_by_email(
#             db,
#             sample_customer_data["contact_email"]
#         )
        
#         assert customer is not None
#         assert customer.business_name == sample_customer_data["business_name"]
    
#     def test_get_customer_by_email_not_found(self, db: Session):
#         """Test retrieving non-existent email returns None."""
#         customer = CustomerService.get_customer_by_email(db, "nonexistent@test.com")
#         assert customer is None



