.PHONY: help install test lint format docker-build docker-run clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make clean        - Clean up generated files"

install:
	pip install -r requirements.txt

test:
	pytest -v --cov=app --cov-report=term --cov-report=html

lint:
	flake8 app.py test_app.py --max-line-length=120 --extend-ignore=E203
	black --check app.py test_app.py
	isort --check-only app.py test_app.py

format:
	black app.py test_app.py
	isort app.py test_app.py

docker-build:
	docker build -t template-api:latest .

docker-run:
	docker run -p 8080:8080 template-api:latest

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
