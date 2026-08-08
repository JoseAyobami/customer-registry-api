from fastapi import status


class TestCustomerRegistration:
    
    def test_register_customer_success(self, client, sample_customer_data):
        response = client.post("/api/v1/customers", json=sample_customer_data)

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["id"] is not None
        assert data["business_name"] == sample_customer_data["business_name"]
        assert data["contact_email"] == sample_customer_data["contact_email"]
        assert data["status"] == "active"

    def test_register_customer_duplicate_email(
        self,
        client,
        sample_customer_data,
    ):
        client.post("/api/v1/customers", json=sample_customer_data)

        duplicate = sample_customer_data.copy()
        duplicate["business_name"] = "Another Company"

        response = client.post(
            "/api/v1/customers",
            json=duplicate,
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_register_customer_invalid_email(
        self,
        client,
        sample_customer_data,
    ):
        sample_customer_data["contact_email"] = "invalid-email"

        response = client.post(
            "/api/v1/customers",
            json=sample_customer_data,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_customer_missing_required_field(self, client):
        response = client.post(
            "/api/v1/customers",
            json={
                "business_name": "Test Company",
                "business_type": "LLC",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCustomerRetrieval:
    """Tests for GET /api/v1/customers/{id}."""

    def test_get_customer_success(
        self,
        client,
        sample_customer_data,
    ):
        created = client.post(
            "/api/v1/customers",
            json=sample_customer_data,
        )

        customer_id = created.json()["id"]

        response = client.get(f"/api/v1/customers/{customer_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == customer_id

    def test_get_customer_not_found(self, client):
        response = client.get(
            "/api/v1/customers/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCustomerListing:
    """Tests for GET /api/v1/customers."""

    def test_list_customers_empty(self, client):
        response = client.get("/api/v1/customers")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total"] == 0
        assert data["count"] == 0
        assert data["items"] == []

    def test_list_customers(self, client, sample_customer_data):
        for i in range(3):
            customer = sample_customer_data.copy()
            customer["business_name"] = f"Company {i}"
            customer["contact_email"] = f"company{i}@example.com"

            client.post("/api/v1/customers", json=customer)

        response = client.get("/api/v1/customers")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 3

    def test_list_customers_pagination(
        self,
        client,
        sample_customer_data,
    ):
        for i in range(5):
            customer = sample_customer_data.copy()
            customer["business_name"] = f"Company {i}"
            customer["contact_email"] = f"page{i}@example.com"

            client.post("/api/v1/customers", json=customer)

        response = client.get("/api/v1/customers?skip=0&limit=2")
        assert response.json()["count"] == 2

        response = client.get("/api/v1/customers?skip=2&limit=2")
        assert response.json()["count"] == 2

        response = client.get("/api/v1/customers?skip=4&limit=2")
        assert response.json()["count"] == 1

    def test_list_customers_filter_by_status(
        self,
        client,
        sample_customer_data,
    ):
        active = sample_customer_data.copy()
        active["business_name"] = "Active Company"
        active["contact_email"] = "active@example.com"
        active["status"] = "active"

        inactive = sample_customer_data.copy()
        inactive["business_name"] = "Inactive Company"
        inactive["contact_email"] = "inactive@example.com"
        inactive["status"] = "inactive"

        client.post("/api/v1/customers", json=active)
        client.post("/api/v1/customers", json=inactive)

        response = client.get("/api/v1/customers?status=active")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1
        assert response.json()["items"][0]["status"] == "active"



class TestCustomerSearch:
    def test_search_customer_by_business_name(
        self,
        client,
        sample_customer_data,
    ):
        customer = sample_customer_data.copy()
        customer["business_name"] = "Tech Solutions Ltd"
        customer["contact_email"] = "tech@example.com"

        client.post("/api/v1/customers", json=customer)

        response = client.get(
            "/api/v1/customers/search/query?q=Tech"
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["business_name"] == "Tech Solutions Ltd"

    def test_search_customer_no_results(self, client):
        response = client.get()

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["count"] == 0
        assert data["items"] == []

    def test_search_customer_requires_query(self, client):
        response = client.get("/api/v1/customers/search/query")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCustomerUpdate:
    def test_update_customer_success(
        self,
        client,
        sample_customer_data,
    ):
        created = client.post(
            "/api/v1/customers",
            json=sample_customer_data,
        )

        customer_id = created.json()["id"]

        response = client.patch(
            f"/api/v1/customers/{customer_id}",
            json={
                "status": "inactive",
                "contact_phone": "555-9999",
            },
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "inactive"
        assert data["contact_phone"] == "555-9999"

    def test_update_customer_not_found(self, client):
        response = client.patch(
            "/api/v1/customers/00000000-0000-0000-0000-000000000000",
            json={
                "status": "inactive",
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_customer_duplicate_email(
        self,
        client,
        sample_customer_data,
    ):
        first = sample_customer_data.copy()
        first["business_name"] = "First Company"
        first["contact_email"] = "first@example.com"

        second = sample_customer_data.copy()
        second["business_name"] = "Second Company"
        second["contact_email"] = "second@example.com"

        response1 = client.post(
            "/api/v1/customers",
            json=first,
        )

        response2 = client.post(
            "/api/v1/customers",
            json=second,
        )

        second_id = response2.json()["id"]

        response = client.patch(
            f"/api/v1/customers/{second_id}",
            json={
                "contact_email": "first@example.com",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_customer_invalid_status(
        self,
        client,
        sample_customer_data,
    ):
        created = client.post(
            "/api/v1/customers",
            json=sample_customer_data,
        )

        customer_id = created.json()["id"]

        response = client.patch(
            f"/api/v1/customers/{customer_id}",
            json={
                "status": "invalid_status",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestOperationalEndpoints:
    """Tests for operational endpoints."""

    def test_health_check(self, client):
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["service"] == "customer-registry-api"
        assert data["status"] in ["healthy", "degraded"]

    def test_root_endpoint(self, client):
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["service"] == "Customer Registry API"
        assert data["docs"] == "/api/docs"
