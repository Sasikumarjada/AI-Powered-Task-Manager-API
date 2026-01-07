# Project Structure

## Complete Directory Layout

```
task-manager-api/
│
├── app/                          # Application package
│   ├── __init__.py              # Package initialization
│   ├── database.py              # Database configuration and session management
│   ├── models.py                # SQLAlchemy ORM models (Task table)
│   ├── schemas.py               # Pydantic validation schemas
│   ├── services.py              # External API integration (AI service)
│   └── exceptions.py            # Custom exception classes
│
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_api.py              # API endpoint tests (21 tests)
│
├── scripts/                      # Utility scripts
│   └── setup.sh                 # Setup helper script
│
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
├── .env.example                  # Environment variables template
├── .env                          # Environment variables (git-ignored)
├── .gitignore                    # Git ignore rules
│
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker image definition
│
├── README.md                     # Main documentation (YOU ARE HERE)
└── PROJECT_STRUCTURE.md          # This file
```

## File Descriptions

### Core Application Files

#### `main.py` (271 lines)
- FastAPI application initialization
- Four REST endpoints (POST, GET, PUT, DELETE)
- Global exception handlers
- Dependency injection setup
- API routing and documentation configuration

**Key Components:**
- `create_task()`: Creates task with AI analysis
- `get_tasks()`: Retrieves tasks with filtering
- `get_task()`: Gets single task by ID
- `update_task()`: Updates task (partial updates supported)
- `delete_task()`: Deletes task
- `health_check()`: Health check endpoint

#### `app/database.py` (39 lines)
- SQLAlchemy engine configuration
- Database connection pooling
- Session management
- Dependency provider for database sessions

**Key Features:**
- Connection pool (10 base + 20 overflow)
- Pre-ping health checks
- Automatic session cleanup

#### `app/models.py` (48 lines)
- SQLAlchemy ORM model for Task table
- Database schema definition
- Index definitions for query optimization

**Indexes:**
- `id` (primary key)
- `title`, `status`, `priority`, `created_at` (single-column)
- `(status, priority)` (composite index)

#### `app/schemas.py` (113 lines)
- Pydantic models for request/response validation
- TaskCreate, TaskUpdate, TaskResponse schemas
- Custom validators for business logic
- Enum definitions for status and priority

**Validation Rules:**
- Title: 1-200 characters, no whitespace-only
- Description: 1-5000 characters, no whitespace-only
- Status: enum (todo, in_progress, done)
- Priority: enum (low, medium, high)

#### `app/services.py` (119 lines)
- External AI API integration
- Anthropic Claude API client
- Retry logic and timeout handling
- Error handling and graceful degradation

**Features:**
- 10-second timeout
- 2 retry attempts
- Structured error handling
- JSON response parsing

#### `app/exceptions.py` (6 lines)
- Custom exception classes
- TaskNotFoundError (404)
- ExternalAPIError (503)

### Testing Files

#### `tests/test_api.py` (299 lines)
- 21 comprehensive tests
- Unit and integration tests
- Mocked external dependencies
- Test fixtures and setup/teardown

**Test Coverage:**
- Task creation (7 tests)
- Task retrieval (6 tests)
- Task update (4 tests)
- Task deletion (2 tests)
- AI service integration (2 tests)

#### `pytest.ini` (11 lines)
- Pytest configuration
- Coverage reporting setup
- Test discovery patterns

### Configuration Files

#### `requirements.txt` (11 lines)
Core dependencies:
- fastapi==0.109.0 (API framework)
- uvicorn[standard]==0.27.0 (ASGI server)
- sqlalchemy==2.0.25 (ORM)
- psycopg2-binary==2.9.9 (PostgreSQL driver)
- pydantic==2.5.3 (validation)
- httpx==0.26.0 (HTTP client)
- pytest==7.4.4 (testing framework)

#### `.env.example` (6 lines)
Environment variable template:
- DATABASE_URL
- ANTHROPIC_API_KEY
- TEST_DATABASE_URL (optional)

#### `docker-compose.yml` (29 lines)
Multi-container Docker setup:
- PostgreSQL service (port 5432)
- API service (port 8000)
- Volume persistence
- Health checks

#### `Dockerfile` (20 lines)
API container image:
- Python 3.11 slim base
- System dependencies (gcc, postgresql-client)
- Python dependencies installation
- Application code

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Client Layer                      │
│          (HTTP Clients, Browsers, Postman)          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Presentation Layer                      │
│                   (main.py)                         │
│  • FastAPI endpoints                                │
│  • Request/Response handling                        │
│  • Global exception handlers                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Validation Layer                        │
│                (schemas.py)                         │
│  • Pydantic models                                  │
│  • Input validation                                 │
│  • Response serialization                           │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌─────────────────┐         ┌─────────────────┐
│ Business Logic  │         │  External API   │
│  (services.py)  │         │   Integration   │
│                 │         │  (services.py)  │
│ • AI analysis   │◄────────┤                 │
│ • Business rules│         │ • Anthropic API │
└────────┬────────┘         └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│             Data Access Layer                        │
│           (database.py, models.py)                  │
│  • SQLAlchemy ORM                                   │
│  • Database sessions                                │
│  • Connection pooling                               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                   PostgreSQL                         │
│              (Database Storage)                      │
└─────────────────────────────────────────────────────┘
```

## Data Flow for POST /tasks

```
1. Client sends POST request with JSON body
   ↓
2. FastAPI receives and routes to create_task()
   ↓
3. Pydantic validates TaskCreate schema
   ↓
4. AIService.analyze_task() called
   ├─→ HTTP request to Anthropic API
   ├─→ Retry logic if timeout/error
   └─→ Parse JSON response
   ↓
5. Create Task model instance with AI data
   ↓
6. SQLAlchemy adds to session and commits
   ↓
7. Database returns task with ID
   ↓
8. Pydantic serializes to TaskWithAI schema
   ↓
9. FastAPI returns 201 Created with JSON
```

## Key Design Patterns

### 1. Dependency Injection
```python
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends()
):
```
**Benefits:** Easy testing, loose coupling, single responsibility

### 2. Repository Pattern (Implicit)
- Database operations centralized in models.py
- Business logic separated from data access
- Easy to swap ORM implementations

### 3. Service Layer Pattern
- External API calls in services.py
- Reusable business logic
- Clear separation of concerns

### 4. Exception Handler Pattern
- Global exception handlers in main.py
- Consistent error responses
- Centralized error logging

### 5. Factory Pattern (Session Management)
```python
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
**Benefits:** Automatic cleanup, consistent session handling

## Performance Considerations

### Database Indexes
```sql
-- Single-column indexes
CREATE INDEX idx_tasks_title ON tasks(title);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

-- Composite index for common query pattern
CREATE INDEX idx_status_priority ON tasks(status, priority);
```

**Query Optimization:**
- `WHERE status = 'todo'` → Uses `idx_tasks_status`
- `WHERE priority = 'high'` → Uses `idx_tasks_priority`
- `WHERE status = 'todo' AND priority = 'high'` → Uses `idx_status_priority`
- `ORDER BY created_at DESC` → Uses `idx_tasks_created_at`

### Connection Pooling
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # 10 persistent connections
    max_overflow=20      # 20 additional connections on demand
)
```

**Capacity:**
- Normal load: 10 concurrent requests
- Peak load: 30 concurrent requests
- Connection lifetime: Automatic recycling

### Async/Await
- Non-blocking I/O for external API calls
- Better concurrency under high load
- Efficient resource utilization

## Security Considerations

### Input Validation
- All inputs validated by Pydantic
- SQL injection prevented by SQLAlchemy ORM
- XSS prevented by JSON responses (no HTML)

### Database
- Prepared statements (SQLAlchemy ORM)
- Connection pooling with pre-ping
- No raw SQL queries

### API Keys
- Stored in environment variables
- Not committed to version control
- Loaded via python-dotenv

### Future Enhancements Needed
- Authentication (JWT)
- Rate limiting
- CORS configuration
- HTTPS enforcement
- API key rotation

## Scalability Path

### Horizontal Scaling
1. Add load balancer (nginx, HAProxy)
2. Run multiple API instances
3. Shared PostgreSQL database
4. Redis for distributed caching

### Vertical Scaling
1. Increase database connection pool
2. Add database read replicas
3. Implement query optimization
4. Add database partitioning

### Microservices Evolution
```
Current: Monolith API
    ↓
Step 1: Extract AI service to separate microservice
    ↓
Step 2: Extract task service
    ↓
Step 3: Add API gateway (Kong, Tyk)
    ↓
Final: Distributed microservices with event bus
```

## Monitoring & Observability

### Logs
- Structured logging with standard library
- Log levels: INFO, WARNING, ERROR
- Logged events:
  - Task creation/update/deletion
  - AI service calls
  - Database errors
  - External API failures

### Metrics (Future)
- Request count and latency
- Database query time
- AI service response time
- Error rates by endpoint

### Health Checks
- `/health` endpoint
- Database connection check (can be added)
- AI service availability check (can be added)

## Development Workflow

### Local Development
```bash
1. source venv/bin/activate
2. uvicorn main:app --reload
3. Edit code (auto-reloads)
4. Run tests: pytest
```

### Docker Development
```bash
1. docker-compose up
2. Edit code (volume mounted)
3. Container auto-reloads
4. docker-compose logs -f api
```

### Testing Workflow
```bash
1. Run tests: pytest
2. Check coverage: pytest --cov
3. Fix failing tests
4. View HTML report: open htmlcov/index.html
```

## CI/CD Pipeline (Recommended)

```yaml
stages:
  - lint
  - test
  - build
  - deploy

lint:
  - flake8 app tests
  - black --check app tests
  - isort --check app tests

test:
  - pytest --cov=app --cov-report=xml
  - coverage threshold: 80%

build:
  - docker build -t task-api:$CI_COMMIT_SHA .
  - docker push task-api:$CI_COMMIT_SHA

deploy:
  - kubectl apply -f k8s/
  - kubectl set image deployment/task-api task-api=task-api:$CI_COMMIT_SHA
```

## Summary

This project demonstrates:
- ✅ Clean architecture with clear separation of concerns
- ✅ Production-ready error handling and resilience
- ✅ Comprehensive testing with high coverage
- ✅ Proper validation at multiple layers
- ✅ External API integration with graceful degradation
- ✅ Docker support for easy deployment
- ✅ Scalable database design with proper indexing
- ✅ Clear documentation and code organization

**Total Lines of Code:**
- Python code: ~850 lines
- Tests: ~300 lines
- Documentation: ~1200 lines
- Configuration: ~100 lines
- **Total: ~2450 lines**
