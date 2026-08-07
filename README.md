# Customer Registry API

A RESTful API for registering, retrieving, searching, and updating business customers.

Built with FastAPI, SQLAlchemy, Alembic, and SQLite. The project follows a layered architecture that separates API routes, business logic, data models, and validation.

---

## Features

- Register business customers
- Retrieve customer by ID
- List customers with pagination and filtering
- Search customers
- Partially update customer records
- Request validation with Pydantic
- Database migrations using Alembic
- Structured logging
- Automated tests with pytest
- Interactive API documentation (Swagger)

---

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- SQLite
- Pydantic
- Pytest

---

## Project Structure

```
customer-registry-api/
│
├── alembic/
├── app/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── tests/
├── run.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Installation

Clone the repository.

```bash
git clone https://github.com/JoseAyobami/peer.git

cd customer-registry-api
```

Create and activate a virtual environment.

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=<your_database_connection_string>
LOG_LEVEL=<log_level>
ENV=<environment>
```



## Database

Run database migrations.

```bash
alembic upgrade head
```

---

## Running the Application

```bash
python run.py
```

or

```bash
uvicorn app.main:app --reload
```

---

## API Documentation

Swagger UI

```
http://localhost:8000/api/docs
```

OpenAPI

```
http://localhost:8000/api/openapi.json
```

Health Check

```
http://localhost:8000/health
```

---

## Running Tests

Run the full test suite.

```bash
pytest
```

Run with verbose output.

```bash
pytest -v
```

Run with coverage.

```bash
pytest --cov=app --cov-report=html
```

---

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/customers` | Register a customer |
| GET | `/api/v1/customers/{id}` | Retrieve customer |
| GET | `/api/v1/customers` | List customers |
| GET | `/api/v1/customers/search/query` | Search customers |
| PATCH | `/api/v1/customers/{id}` | Update customer |
| GET | `/health` | Health check |

---

## Design

The application follows a layered architecture.

- Routes handle HTTP requests.
- Services contain business logic.
- Schemas validate request and response data.
- Models define database tables.
- Alembic manages schema migrations.

---

## Testing

The project includes tests covering:

- Customer registration
- Customer retrieval
- Search
- Pagination
- Updates
- Validation
- Error handling
- Health endpoint

---

## Future Improvements

- Authentication and authorization
- Rate limiting
- PostgreSQL support
- Docker support
- CI/CD pipeline
- Audit logging
- Soft delete
- Redis caching

---

## License

This project is provided for educational and assessment purposes.