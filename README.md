# Python API Template

A production-ready FastAPI REST API template with best practices, comprehensive testing, CI/CD, and Docker support.

## Features

- ✅ **FastAPI** - Modern, fast web framework for building APIs
- ✅ **Pydantic** - Data validation using Python type annotations
- ✅ **Comprehensive Tests** - Unit tests with pytest and 100% coverage goal
- ✅ **GitHub Actions** - CI/CD pipeline for testing, linting, and Docker builds
- ✅ **Docker** - Multi-stage builds with health checks
- ✅ **API Documentation** - Auto-generated OpenAPI (Swagger) docs
- ✅ **Health Checks** - Kubernetes-ready liveness and readiness probes
- ✅ **Error Handling** - Comprehensive error handling with meaningful responses
- ✅ **Logging** - Structured logging configuration
- ✅ **Type Safety** - Full type hints throughout the codebase
- ✅ **Pagination** - Built-in pagination support
- ✅ **CORS** - Configurable CORS middleware
- ✅ **Environment Configuration** - `.env` file support

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone git@github.com:takabayashi-demos/template-api.git
   cd template-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:8080`
   
   - API Documentation: `http://localhost:8080/docs`
   - Alternative docs: `http://localhost:8080/redoc`
   - OpenAPI Schema: `http://localhost:8080/openapi.json`

### Using Docker

1. **Build and run with Docker**
   ```bash
   docker build -t template-api:latest .
   docker run -p 8080:8080 template-api:latest
   ```

2. **Or use Docker Compose**
   ```bash
   docker-compose up
   ```

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest test_app.py

# Run specific test class or function
pytest test_app.py::TestHealthEndpoints::test_health_endpoint
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=term --cov-report=html

# View HTML coverage report
open htmlcov/index.html  # On macOS
```

## API Endpoints

### Health Checks

- **GET /health** - Service health check
  ```bash
  curl http://localhost:8080/health
  ```
  Response:
  ```json
  {
    "status": "UP",
    "service": "template-api",
    "timestamp": "2024-01-01T00:00:00.000000",
    "version": "1.0.0"
  }
  ```

- **GET /ready** - Readiness check for Kubernetes
  ```bash
  curl http://localhost:8080/ready
  ```

### Items API

- **GET /api/v1/items** - List all items (paginated)
  ```bash
  curl "http://localhost:8080/api/v1/items?limit=10&offset=0"
  ```

- **GET /api/v1/items/{id}** - Get item by ID
  ```bash
  curl http://localhost:8080/api/v1/items/1
  ```

- **POST /api/v1/items** - Create new item
  ```bash
  curl -X POST http://localhost:8080/api/v1/items \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Example Item",
      "description": "Item description"
    }'
  ```

- **PUT /api/v1/items/{id}** - Update item
  ```bash
  curl -X PUT http://localhost:8080/api/v1/items/1 \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Updated Item",
      "description": "New description"
    }'
  ```

- **DELETE /api/v1/items/{id}** - Delete item
  ```bash
  curl -X DELETE http://localhost:8080/api/v1/items/1
  ```

## Configuration

Configure the application using environment variables in `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8080` |
| `DEBUG` | Enable debug mode | `false` |
| `APP_VERSION` | Application version | `1.0.0` |

Example `.env` file:
```env
PORT=8080
APP_VERSION=1.0.0
DEBUG=false
```

## Project Structure

```
template-api/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD
├── app.py                      # Main application
├── test_app.py                 # Unit tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── pytest.ini                  # Pytest configuration
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **Tests** - Runs on Python 3.10 and 3.11
   - Executes all unit tests
   - Generates coverage reports
   - Uploads to Codecov

2. **Linting** - Code quality checks
   - Flake8 for style compliance
   - Black for code formatting
   - isort for import sorting
   - mypy for type checking

3. **Docker** - Container validation
   - Builds Docker image
   - Tests container health
   - Caches layers for faster builds

## Development

### Code Style

This project follows PEP 8 style guidelines:

```bash
# Format code with black
black app.py test_app.py

# Sort imports with isort
isort app.py test_app.py

# Check with flake8
flake8 app.py test_app.py --max-line-length=120
```

### Adding New Endpoints

1. Define Pydantic models for request/response
2. Add route handler with type hints
3. Include proper error handling
4. Add logging for important operations
5. Write unit tests
6. Update API documentation

Example:
```python
from pydantic import BaseModel

class NewModel(BaseModel):
    field: str

@app.post("/api/v1/resource", response_model=NewModel)
async def create_resource(data: NewModel):
    # Implementation
    return data
```

### Database Integration

To add database support:

1. Install database driver:
   ```bash
   pip install sqlalchemy asyncpg  # For PostgreSQL
   ```

2. Create database models and connection
3. Update `.env.example` with database URL
4. Add database health check to `/ready` endpoint
5. Update tests to use test database

## Production Deployment

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: template-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: template-api
  template:
    metadata:
      labels:
        app: template-api
    spec:
      containers:
      - name: api
        image: template-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: PORT
          value: "8080"
        - name: APP_VERSION
          value: "1.0.0"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Docker Compose Production

```yaml
version: '3.8'

services:
  api:
    image: template-api:latest
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - APP_VERSION=1.0.0
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8080/docs`
  - Interactive API testing
  - Request/response examples
  - Try out endpoints directly

- **ReDoc**: `http://localhost:8080/redoc`
  - Clean, readable documentation
  - Better for documentation sharing

- **OpenAPI Schema**: `http://localhost:8080/openapi.json`
  - Machine-readable API specification
  - Use for code generation

## Performance

FastAPI provides excellent performance:
- Async/await support for concurrent requests
- Automatic request validation
- Fast JSON serialization
- Built-in response caching support

### Scaling

- Increase `--workers` in Dockerfile for more processes
- Use `uvicorn[standard]` for better performance
- Add Redis for caching
- Implement connection pooling for databases

## Security Best Practices

- ✅ Input validation with Pydantic
- ✅ Type safety throughout
- ✅ Environment variable configuration
- ✅ Health check endpoints don't expose sensitive data
- 🔜 Add authentication (JWT, OAuth2)
- 🔜 Add rate limiting
- 🔜 Add CORS configuration
- 🔜 Add request logging/monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - feel free to use this template for your projects.

## Support

For issues and questions, please open an issue on GitHub.
