"""
Unit tests for the Template API
"""
import pytest
from fastapi.testclient import TestClient
from app import app, items_db, item_counter


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test"""
    global items_db, item_counter
    items_db.clear()
    globals()['item_counter'] = 0
    yield
    items_db.clear()


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_endpoint(self, client):
        """Test /health endpoint returns UP status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert data["service"] == "template-api"
        assert "timestamp" in data
        assert "version" in data

    def test_ready_endpoint(self, client):
        """Test /ready endpoint returns READY status"""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "READY"
        assert "timestamp" in data


class TestItemsAPI:
    """Test items CRUD operations"""

    def test_get_items_empty(self, client):
        """Test GET /api/v1/items returns empty list initially"""
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["limit"] == 50
        assert data["offset"] == 0

    def test_create_item(self, client):
        """Test POST /api/v1/items creates a new item"""
        payload = {
            "name": "Test Item",
            "description": "This is a test item"
        }
        response = client.post("/api/v1/items", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Item"
        assert data["description"] == "This is a test item"
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_item_without_description(self, client):
        """Test POST /api/v1/items works without description"""
        payload = {"name": "Test Item"}
        response = client.post("/api/v1/items", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["description"] == ""

    def test_create_item_validation_error(self, client):
        """Test POST /api/v1/items with invalid data returns 422"""
        payload = {"description": "Missing name"}
        response = client.post("/api/v1/items", json=payload)
        assert response.status_code == 422

    def test_get_item_by_id(self, client):
        """Test GET /api/v1/items/:id returns specific item"""
        # Create an item first
        payload = {"name": "Test Item", "description": "Description"}
        create_response = client.post("/api/v1/items", json=payload)
        item_id = create_response.json()["id"]

        # Get the item
        response = client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Test Item"

    def test_get_item_not_found(self, client):
        """Test GET /api/v1/items/:id returns 404 for non-existent item"""
        response = client.get("/api/v1/items/999")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["error"].lower()

    def test_update_item(self, client):
        """Test PUT /api/v1/items/:id updates an item"""
        # Create an item first
        payload = {"name": "Original Name", "description": "Original Description"}
        create_response = client.post("/api/v1/items", json=payload)
        item_id = create_response.json()["id"]

        # Update the item
        update_payload = {"name": "Updated Name", "description": "Updated Description"}
        response = client.put(f"/api/v1/items/{item_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated Description"

    def test_update_item_partial(self, client):
        """Test PUT /api/v1/items/:id with partial update"""
        # Create an item first
        payload = {"name": "Original Name", "description": "Original Description"}
        create_response = client.post("/api/v1/items", json=payload)
        item_id = create_response.json()["id"]

        # Update only the name
        update_payload = {"name": "Updated Name"}
        response = client.put(f"/api/v1/items/{item_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Original Description"

    def test_update_item_not_found(self, client):
        """Test PUT /api/v1/items/:id returns 404 for non-existent item"""
        update_payload = {"name": "Updated Name"}
        response = client.put("/api/v1/items/999", json=update_payload)
        assert response.status_code == 404

    def test_delete_item(self, client):
        """Test DELETE /api/v1/items/:id deletes an item"""
        # Create an item first
        payload = {"name": "Test Item"}
        create_response = client.post("/api/v1/items", json=payload)
        item_id = create_response.json()["id"]

        # Delete the item
        response = client.delete(f"/api/v1/items/{item_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_item_not_found(self, client):
        """Test DELETE /api/v1/items/:id returns 404 for non-existent item"""
        response = client.delete("/api/v1/items/999")
        assert response.status_code == 404

    def test_get_items_pagination(self, client):
        """Test GET /api/v1/items with pagination"""
        # Create multiple items
        for i in range(15):
            client.post("/api/v1/items", json={"name": f"Item {i}"})

        # Test pagination
        response = client.get("/api/v1/items?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 15
        assert data["limit"] == 5
        assert data["offset"] == 0

        # Test second page
        response = client.get("/api/v1/items?limit=5&offset=5")
        data = response.json()
        assert len(data["items"]) == 5
        assert data["offset"] == 5

    def test_get_items_pagination_limits(self, client):
        """Test GET /api/v1/items respects pagination limits"""
        # Test max limit
        response = client.get("/api/v1/items?limit=300")
        assert response.status_code == 422  # Exceeds max limit

        # Test min limit
        response = client.get("/api/v1/items?limit=0")
        assert response.status_code == 422  # Below min limit


class TestDocumentation:
    """Test API documentation endpoints"""

    def test_openapi_schema(self, client):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "Template API"
        assert "paths" in schema

    def test_docs_endpoint(self, client):
        """Test Swagger UI documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert b"swagger" in response.content.lower()
