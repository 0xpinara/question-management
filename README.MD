# Question Management API

FastAPI-based REST API for managing educational questions with metadata, caching, and PostgreSQL storage.

## Features
- Full CRUD operations for questions
- Metadata management with Redis caching
- Pagination and filtering support
- Text search capabilities
- Docker containerization

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Installation & Running
1. Clone the repository:
git clone <https://github.com/0xpinara/question-management>


2. Start the services:
docker-compose up --build


3. The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs


## API Endpoints

### Questions
- `GET /api/v1/questions`: List questions (with pagination & filters)
- `POST /api/v1/questions`: Create question
- `GET /api/v1/questions/{id}`: Get question
- `PUT /api/v1/questions/{id}`: Update question
- `DELETE /api/v1/questions/{id}`: Delete question

### Filters
- Difficulty level (basic, intermediate, advanced)
- Cognitive level (knowledge, comprehension, etc.)
- Course name
- Context pages
- Text search

### Metadata
- `GET /api/v1/metadata`: Get metadata stats

## Tech Stack
- Python 3.9
- FastAPI
- PostgreSQL
- Redis (caching)
- Docker & Docker Compose
- SQLAlchemy
- Alembic

## Project Structure
question_management/
├── app/
│ ├── models/ # Database models
│ ├── routes/ # API endpoints
│ ├── schemas/ # Pydantic models
│ └── utils/ # Utility functions
├── data/ # Sample data
├── docker-compose.yml
└── Dockerfile


## Error Handling
- 404: Resource not found
- 400: Bad request (validation errors)
- 500: Server errors

## Caching Strategy
Redis is used for caching with the following configuration:
- Maximum memory: 512MB
- Eviction policy: allkeys-lru
- Persistence: AOF enabled
