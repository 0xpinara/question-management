from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.models.models import Question, Metadata
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse, MetadataResponse
from fastapi_cache.decorator import cache
from sqlalchemy import or_
from app.utils.data_loader import get_coverage_statistics, get_questions_by_page
from app.utils.metadata_updater import update_metadata
from fastapi_cache import FastAPICache

router = APIRouter()

@router.get("/questions", 
    response_model=dict,
    description="Get questions with optional filtering and pagination")
async def get_questions(
    db: Session = Depends(get_db),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(10, description="Number of records to return"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    cognitive_level: Optional[str] = Query(None, description="Filter by cognitive level"),
    course_name: Optional[str] = Query(None, description="Filter by course name"),
    context_pages: Optional[List[int]] = Query(None, description="Filter by context pages"),
    search: Optional[str] = Query(None, description="Search in question text")
):
    query = db.query(Question)
    
    if difficulty_level:
        query = query.filter(Question.difficulty_level == difficulty_level)
    if cognitive_level:
        query = query.filter(Question.cognitive_level == cognitive_level)
    if course_name:
        query = query.filter(Question.course_name == course_name)
    if context_pages:
        query = query.filter(Question.context_pages.overlap(context_pages))
    if search:
        query = query.filter(
            or_(
                Question.question_text.ilike(f"%{search}%"),
                Question.course_name.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    questions = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "questions": [QuestionResponse.from_orm(q) for q in questions],
        "skip": skip,
        "limit": limit
    }

@router.post("/questions", 
    response_model=QuestionResponse,
    status_code=201,
    description="Create a new question")
async def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = Question(**question.model_dump())
    try:
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        # Update metadata and invalidate cache
        update_metadata(db)
        await FastAPICache.clear()
        return db_question
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/questions/{question_id}", 
    response_model=QuestionResponse,
    description="Get a specific question by ID")
@cache(expire=60)
async def get_question(question_id: str, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.put("/questions/{question_id}", 
    response_model=QuestionResponse,
    description="Update a question by ID")
async def update_question(
    question_id: str, 
    question_update: QuestionUpdate, 
    db: Session = Depends(get_db)
):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    update_data = question_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_question, field, value)
    
    try:
        db.commit()
        db.refresh(db_question)
        # Update metadata and invalidate cache
        update_metadata(db)
        await FastAPICache.clear()
        return db_question
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/questions/{question_id}", 
    status_code=204,
    description="Delete a question by ID")
async def delete_question(question_id: str, db: Session = Depends(get_db)):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    try:
        db.delete(db_question)
        db.commit()
        # Update metadata and invalidate cache
        update_metadata(db)
        await FastAPICache.clear()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metadata", 
    response_model=MetadataResponse,
    description="Get metadata about questions")
@cache(expire=300)
async def get_metadata(db: Session = Depends(get_db)):
    metadata = db.query(Metadata).first()
    if not metadata:
        # If metadata doesn't exist, create it
        try:
            metadata = update_metadata(db)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error creating metadata: {str(e)}"
            )
    return metadata

@router.get("/questions/by-page/{page_number}",
    response_model=dict,
    description="Get questions by page number")
async def get_questions_for_page(
    page_number: int,
    db: Session = Depends(get_db)
):
    try:
        questions = get_questions_by_page(db, page_number)
        return {
            "page_number": page_number,
            "questions": [QuestionResponse.from_orm(q) for q in questions]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/coverage-statistics",
    response_model=dict,
    description="Get coverage statistics for the course content")
@cache(expire=300)
async def get_coverage_stats(db: Session = Depends(get_db)):
    try:
        stats = get_coverage_statistics(db)
        if not stats:
            raise HTTPException(
                status_code=404,
                detail="No coverage statistics available"
            )
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting coverage statistics: {str(e)}"
        )