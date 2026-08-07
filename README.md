# Customer Registry API

  "id": "550e8400-e29b-41d4-a716-446655440000",

## Quick Start

### Prerequisites
- Python 3.9+
- pip or poetry

### Setup and Run

```bash
# Clone or navigate to project directory
cd customer-registry-api

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run the server (includes setup, tests, and startup)
python run.py
```

The API will be available at `http://localhost:8000`
- **API Docs:** http://localhost:8000/api/docs (interactive Swagger UI)
- **Health Check:** http://localhost:8000/health
- **Root Info:** http://localhost:8000/

### Run Tests Only

```bash
pytest tests/ -v
```

## Architecture

### Directory Structure

```
customer-registry-api/
├── app/
│   ├── models/           # SQLAlchemy database models
│   │   └── customer.py   # Customer entity
│   ├── schemas/          # Pydantic validation schemas
│   │   └── customer.py   # Request/response contracts
│   ├── services/         # Business logic layer
│   │   └── customer_service.py
│   ├── routes/           # API endpoints
│   │   └── customers.py  # Customer endpoints
│   ├── config.py         # Configuration management
│   ├── database.py       # Database setup & session mgmt
│   └── main.py           # FastAPI application factory
├── tests/
│   ├── conftest.py       # Pytest fixtures & configuration
│   └── test_endpoints.py # Integration tests
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── run.py               # Startup script
```

### Design Principles

1. **Clear Boundaries:** Service layer handles business rules, routes handle HTTP concerns
2. **Validation at Entry:** Pydantic schemas validate all inputs with clear error messages
3. **Data Integrity:** Database unique constraints + application-level checks for duplicates
4. **Audit Trail:** Created/updated timestamps on all records
5. **Predictable Errors:** Consistent error response format with error codes and messages
6. **Structured Logging:** All important operations logged for operational visibility

## API Endpoints

### Register Customer (Create)

```http
POST /api/v1/customers
Content-Type: application/json
Idempotency-Key: customer-001

{
  "business_name": "Acme Corporation",
  "business_type": "corporation",
  "industry": "Technology",
  "contact_email": "contact@acme.com",
  "contact_phone": "+1-555-0100",
  "status": "active"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "business_name": "Acme Corporation",
  "business_type": "corporation",
  "industry": "Technology",
  "contact_email": "contact@acme.com",
  "contact_phone": "+1-555-0100",
  "status": "active",
  "created_at": "2026-08-04T10:30:00",
  "updated_at": "2026-08-04T10:30:00"
}
```

**Validation Rules:**
- `business_name`: Required, 1-255 characters
- `business_type`: Required, one of: corporation, partnership, llc, sole_proprietorship, non_profit, other
- `industry`: Required, 1-100 characters
- `contact_email`: Required, valid email format, must be unique
- `contact_phone`: Optional, max 20 characters
- `status`: Optional (defaults to "active"), must be one of: active, inactive, pending

**Error Responses:**
- `409 Conflict`: Duplicate customer or conflicting idempotency key
- `422 Unprocessable Entity`: Validation failure

---

### Get Customer by ID

```http
GET /api/v1/customers/{customer_id}
```

**Response (200 OK):**
Same as register response above

**Error Responses:**
- `404 Not Found`: Customer not found

---

### List All Customers

```http
GET /api/v1/customers?skip=0&limit=100&status=active
```

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Maximum results (default: 100, max: 1000)
- `q`: Optional general search term
- `business_type`: Optional filter by business type
- `industry`: Optional partial industry filter
- `status`: Optional filter by status (active, inactive, pending)

**Response (200 OK):**
```json
{
  "total": 42,
  "count": 10,
  "items": [
    {
      "id": 1,
      "business_name": "Acme Corporation",
      ...
    },
    ...
  ]
}
```

---

### Search Customers

```http
GET /api/v1/customers/search/query?q=acme&skip=0&limit=100
```

Searches across:
- Business name (case-insensitive partial match)
- Contact email
- Contact phone

**Query Parameters:**
- `q`: Search term (required, 1-255 characters)
- `skip`: Pagination offset (default: 0)
- `limit`: Maximum results (default: 100, max: 1000)

**Response (200 OK):**
```json
{
  "total": 3,
  "count": 3,
  "items": [...]
}
```

---

### Update Customer (Partial Update)

```http
PATCH /api/v1/customers/{customer_id}
Content-Type: application/json

{
  "status": "inactive",
  "contact_phone": "+1-555-0200"
}
```

**All fields optional.** Only provided fields are updated.

**Response (200 OK):**
Updated customer object (see register response)

**Validation:**
- Email uniqueness enforced (cannot update to email already in use)
- `contact_email` can be changed and is checked for duplicates

**Error Responses:**
- `404 Not Found`: Customer not found
- `409 Conflict`: Duplicate customer or duplicate email

---

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "customer-registry-api",
  "database": "ok"
}
```

Status values: `"healthy"` (database OK), `"degraded"` (database error)

---

## Data Model

### Customer Entity

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID string | Primary Key | Auto-generated |
| business_name | String(255) | NOT NULL, Indexed | Legal business name |
| business_type | String(100) | NOT NULL | Type: corporation, partnership, llc, sole_proprietorship, non_profit, other |
| industry | String(100) | NOT NULL | Industry classification |
| contact_email | String(255) | NOT NULL, UNIQUE, Indexed | Primary contact email |
| contact_phone | String(20) | Nullable | Optional contact phone |
| status | String(20) | NOT NULL, Default: "active", Indexed | active, inactive, or pending |
| created_at | DateTime | NOT NULL, Indexed | Audit timestamp |
| updated_at | DateTime | NOT NULL | Last modification timestamp |

**Database:** SQLite by default (configured in .env via `DATABASE_URL`)

**Indexes:**
- `idx_business_name` - for listing and filtering
- `idx_contact_email` - for duplicate detection and search
- `idx_status` - for status filtering
- `idx_business_name_status` - for combined queries
- `idx_industry_status` - for industry filtering

## Testing

### Test Coverage

The test suite covers:

1. **Happy Path**
   - Register customer with all fields
   - Register with minimal required fields
   - Retrieve customer by ID
   - List customers with pagination
   - Search across name, email, phone
   - Update single and multiple fields

2. **Validation & Constraints**
   - Email format validation
   - Required field validation
   - Status enum validation
   - Business name minimum length
   - Duplicate email detection
   - Duplicate email on update

3. **Error Cases**
   - Non-existent customer retrieval
   - Duplicate email registration
   - Invalid status values
   - Missing required fields
   - Invalid email format

4. **Edge Cases**
   - Empty customer list
   - Search with no results
   - Case-insensitive search
   - Pagination boundaries
   - Status filtering

5. **Operational**
   - Health check endpoint
   - Root information endpoint

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_endpoints.py -v

# Run specific test
pytest tests/test_endpoints.py::TestCustomerRegistration::test_register_customer_success -v
```

**Test Database:** Tests use an in-memory SQLite database (isolated per test)

## Error Handling

### Error Response Format

All error responses follow a consistent contract:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "additional": "context"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `DUPLICATE_CUSTOMER` | 409 | Duplicate business identity or email |
| `NOT_FOUND` | 404 | Customer not found |
| `INVALID_UPDATE` | 400 | Cannot apply update (e.g., duplicate email) |
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Safe Error Messages

- Validation errors detail which fields failed
- Duplicate errors do not leak existing customer data
- Not found errors include the ID that was requested
- All 500 errors are logged internally for debugging

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Database connection string
DATABASE_URL=sqlite:///./customers.db

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Environment: development, staging, production
ENV=development
```

### Database Setup

Database tables are automatically created on application startup. No manual migration required.

To reset the database:
```bash
rm customers.db  # Delete SQLite file
# Restart application - tables will be recreated
```

## Performance & Scalability

### Current State
- SQLite for simplicity (suitable for single-process development)
- Indexed fields for common queries
- Pagination limits (max 1000 per request)
- Connection pooling via SQLAlchemy

### Production Considerations (Deferred)

For production deployments:
1. **Database:** Switch to PostgreSQL or MySQL via `DATABASE_URL`
2. **Scaling:** Multi-process with Gunicorn/Uvicorn
3. **Caching:** Redis for search results or frequently accessed customers
4. **Connection Pooling:** Increase pool size, tune timeouts
5. **Metrics:** Add Prometheus endpoints for monitoring
6. **Rate Limiting:** Implement per-client rate limits
7. **Authentication:** Add OAuth2/API key authentication
8. **Audit Logging:** Store all changes in audit table for compliance

## Assumptions & Trade-offs

### Assumptions Made

1. **Email as Unique Identifier:** Assumed each business has one primary email
2. **Soft Deletes Not Required:** No deleted_at field; status flag sufficient
3. **Single-Process Deployment:** No distributed transaction concerns
4. **SQLite Suitable:** Assumes single-server deployment for now
5. **No Authentication:** Internal service; no auth layer implemented
6. **Synthetic Data Only:** All test data is non-production

### Trade-offs

| Choice | Rationale | Alternative |
|--------|-----------|-------------|
| Pydantic for validation | Type safety + clear contracts | Manual validation |
| SQLAlchemy ORM | Productivity, migrations, type hints | Raw SQL queries |
| SQLite | Minimal setup, no external deps | PostgreSQL (requires setup) |
| In-memory test DB | Fast isolated tests | Separate test database |
| Simple timestamps | Audit trail sufficiency | Full audit table with user tracking |
| No soft deletes | Simpler model, status flag sufficient | Soft delete pattern |

## Operational Notes

### Logging

Logs include:
- Customer creation/update events
- Duplicate email attempts
- Search queries executed
- Database health check results
- Validation errors

Example log entry:
```
2026-08-04 10:30:00,000 - app.services.customer_service - INFO - Customer created: id=1, email=contact@acme.com
```

### Monitoring

Health endpoint can be polled for:
- API availability
- Database connectivity

```bash
curl http://localhost:8000/health
```

### Debugging

Enable debug logging:
```env
LOG_LEVEL=DEBUG
ENV=development
```

### Known Limitations (Deferred Work)

1. **No Batch Operations:** Single customer at a time (consider bulk register endpoint)
2. **No Delete Endpoint:** Customers cannot be removed (consider soft-delete pattern)
3. **No Versioning:** API is v1 only; version strategy for future APIs deferred
4. **No Authentication:** Any client can register/update customers
5. **No Rate Limiting:** No protection against repeated requests
6. **No Audit Logging:** Changes not logged separately (rely on updated_at)
7. **No Search Filters:** Search doesn't filter by status/industry
8. **No Advanced Filtering:** Cannot search with AND/OR conditions

## Deployment

### Local Development

```bash
python run.py
```

### Production (Nginx/Gunicorn Example)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn app.main:app -w 4 -b 0.0.0.0:8000
```

### Docker (Not Included)

Would add `Dockerfile` and `docker-compose.yml` for containerized deployment.

## Troubleshooting

### Database locked error
- SQLite single-writer limitation; use PostgreSQL for multi-process
- Kill any lingering Python processes

### Port 8000 already in use
```bash
# Use different port
uvicorn app.main:app --port 8001
```

### Tests fail with import errors
```bash
# Ensure working directory is project root
cd customer-registry-api
python -m pytest tests/
```

## Support & Documentation

- **Interactive Docs:** http://localhost:8000/api/docs
- **Telemetry:** `curl http://localhost:8000/health`
- **Source Code:** Well-commented, organized by concern

## Submission Checklist

- [x] **Working Service** - Runnable, complete main workflow
- [x] **API & Data Design** - Clear contracts, validation, persistence
- [x] **Source Repository** - Readable modules, explicit dependencies
- [x] **Tests** - Happy path, validation, edge cases
- [x] **README & Walkthrough** - Setup guide, examples, decisions, trade-offs
- [x] **Health Check** - Operational endpoint included
- [x] **Structured Logs** - Important operations logged
- [x] **Setup & Migrations** - Auto-creates tables on startup
- [x] **API Documentation** - Swagger UI + concise endpoint docs

## Time Accounting

- Project setup & structure: 30 min
- Models, schemas, service layer: 60 min
- API routes & error handling: 45 min
- Tests (36 test cases): 75 min
- Documentation & run script: 30 min
- **Total: ~240 minutes (4 hours)**

Well within the 8-hour budget with room for enhancements.

## AI Disclosure

GitHub Copilot was used to:
- Suggest code structure and patterns
- Generate boilerplate FastAPI route scaffolding
- Help draft test cases
- Assist with documentation formatting

**Final decisions and implementation are my own.** All code reviewed for correctness, security, and alignment with requirements before inclusion.

---

**Last Updated:** August 4, 2026
**Version:** 1.0.0
**Status:** Ready for review and testing
