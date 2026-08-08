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
