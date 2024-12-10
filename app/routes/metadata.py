from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..config.database import get_db  # Update this import path
from ..models.models import Question

router = APIRouter()

@router.get("/metadata")
def get_metadata(db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        # Get total questions count
        total_questions = db.query(Question).count()
        
        # Get unique course names
        course_names = [name[0] for name in db.query(Question.course_name).distinct().all()]
        
        # Get unique difficulty levels
        difficulties = [level[0] for level in db.query(Question.difficulty_level).distinct().all()]
        
        # Get unique cognitive levels
        cognitions = [level[0] for level in db.query(Question.cognitive_level).distinct().all()]
        
        # Get unique covered pages
        covered_pages = sorted(list(set(
            page 
            for pages in db.query(Question.context_pages).all() 
            for page in pages[0]
        )))
        
        return {
            "total_questions": total_questions,
            "courses": course_names,
            "difficulty_levels": difficulties,
            "cognitive_levels": cognitions,
            "covered_pages": covered_pages,
            "api_version": "1.0.0"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving metadata: {str(e)}"
        )