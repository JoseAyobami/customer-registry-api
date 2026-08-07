"""Test configuration and fixtures."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.customer import Customer


# Use in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a clean database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency."""
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_customer_data():
    """Sample customer data for tests."""
    return {
        "business_name": "Acme Corporation",
        "business_type": "corporation",
        "industry": "Technology",
        "contact_email": "contact@acme.com",
        "contact_phone": "+1-555-0100",
        "status": "active",
    }


@pytest.fixture
def sample_customer_minimal():
    """Minimal customer data (no phone)."""
    return {
        "business_name": "Tech Startup Inc",
        "business_type": "llc",
        "industry": "Software",
        "contact_email": "hello@techstartup.io",
    }
