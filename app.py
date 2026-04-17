"""
Python API Template - FastAPI
A production-ready FastAPI REST API template with best practices.
"""
import os
import logging
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic models
class Item(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    created_at: str
    updated_at: str


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class ItemList(BaseModel):
    items: List[Item]
    total: int
    limit: int
    offset: int


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    version: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    status: int


# In-memory data store
items_db = []
item_counter = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    logger.info("Starting API server")
    yield
    logger.info("Shutting down API server")


# Create FastAPI app
app = FastAPI(
    title="Template API",
    description="A production-ready FastAPI template with best practices",
    version=os.environ.get('APP_VERSION', '1.0.0'),
    lifespan=lifespan
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "message": str(exc.detail),
            "status": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status": 500
        }
    )


# Health check endpoints
@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "UP",
        "service": "template-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": os.environ.get('APP_VERSION', '1.0.0')
    }


@app.get("/ready", response_model=HealthResponse, tags=["health"])
async def ready():
    """Readiness check endpoint for Kubernetes"""
    return {
        "status": "READY",
        "service": "template-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": os.environ.get('APP_VERSION', '1.0.0')
    }


# API routes
@app.get("/api/v1/items", response_model=ItemList, tags=["items"])
async def get_items(
    limit: int = Query(50, ge=1, le=200, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
):
    """Get all items with optional pagination"""
    paginated_items = items_db[offset:offset + limit]

    return {
        "items": paginated_items,
        "total": len(items_db),
        "limit": limit,
        "offset": offset
    }


@app.get("/api/v1/items/{item_id}", response_model=Item, tags=["items"])
async def get_item(item_id: int):
    """Get a specific item by ID"""
    item = next((item for item in items_db if item["id"] == item_id), None)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )

    return item


@app.post("/api/v1/items", response_model=Item, status_code=201, tags=["items"])
async def create_item(item: ItemCreate):
    """Create a new item"""
    global item_counter

    try:
        item_counter += 1
        now = datetime.utcnow().isoformat()

        new_item = {
            "id": item_counter,
            "name": item.name,
            "description": item.description or "",
            "created_at": now,
            "updated_at": now
        }

        items_db.append(new_item)
        logger.info(f"Created item: {new_item['id']}")

        return new_item

    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create item"
        )


@app.put("/api/v1/items/{item_id}", response_model=Item, tags=["items"])
async def update_item(item_id: int, item_update: ItemUpdate):
    """Update an existing item"""
    item = next((item for item in items_db if item["id"] == item_id), None)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )

    # Update fields
    if item_update.name is not None:
        item["name"] = item_update.name
    if item_update.description is not None:
        item["description"] = item_update.description

    item["updated_at"] = datetime.utcnow().isoformat()

    logger.info(f"Updated item: {item_id}")

    return item


@app.delete("/api/v1/items/{item_id}", status_code=204, tags=["items"])
async def delete_item(item_id: int):
    """Delete an item"""
    global items_db

    item = next((item for item in items_db if item["id"] == item_id), None)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )

    items_db = [item for item in items_db if item["id"] != item_id]

    logger.info(f"Deleted item: {item_id}")

    return None


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=os.environ.get("DEBUG", "false").lower() == "true"
    )
