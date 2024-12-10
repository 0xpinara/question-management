from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.routes import q, metadata
from app.utils.data_loader import load_questions
from app.models.base import create_tables
import os

# Initialize FastAPI with metadata
app = FastAPI(
    title="Question Management API",
    description="API for managing educational questions and their metadata",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "questions",
            "description": "Operations with questions"
        },
        {
            "name": "metadata",
            "description": "Operations with metadata"
        },
        {
            "name": "root",
            "description": "Root endpoint"
        }
    ]
)

# Create database tables
create_tables()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(
    q.router,
    prefix="/api/v1",
    tags=["questions"]
)
app.include_router(
    metadata.router,
    prefix="/api/v1",
    tags=["metadata"]
)

@app.on_event("startup")
async def startup_event():
    """Initialize cache and load initial data."""
    try:
        # Initialize Redis cache
        redis = aioredis.from_url(
            "redis://redis:6379",
            encoding="utf8",
            decode_responses=True
        )
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        
        # Load initial data
        data_dir = "data"
        for i in range(1, 7):
            file_path = os.path.join(data_dir, f"q{i}.json")
            if os.path.exists(file_path):
                load_questions(file_path)
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise

@app.middleware("http")
async def add_charset_middleware(request: Request, call_next):
    """Add charset to Content-Type header."""
    response = await call_next(request)
    if "Content-Type" not in response.headers:
        response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.get("/", tags=["root"])
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "Question Management API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 Not Found errors."""
    return JSONResponse(
        status_code=404,
        content={"message": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 Internal Server Error."""
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred"}
    )