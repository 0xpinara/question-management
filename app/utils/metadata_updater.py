from sqlalchemy.orm import Session
from app.models.models import Question, Metadata
from sqlalchemy import func
from typing import Dict

def update_metadata(db: Session) -> Metadata:
    """
    Updates or creates metadata about questions in the database
    """
    try:
        # Calculate statistics
        total_questions = db.query(Question).count()
        
        # Get counts for each category
        difficulty_counts = dict(db.query(
            Question.difficulty_level,
            func.count(Question.id)
        ).group_by(Question.difficulty_level).all())
        
        cognitive_counts = dict(db.query(
            Question.cognitive_level,
            func.count(Question.id)
        ).group_by(Question.cognitive_level).all())
        
        course_counts = dict(db.query(
            Question.course_name,
            func.count(Question.id)
        ).group_by(Question.course_name).all())
        
        # Get all unique pages
        all_pages = set()
        for pages in db.query(Question.context_pages).all():
            all_pages.update(pages[0])
        covered_pages = sorted(list(all_pages))
        
        # Create or update metadata
        metadata = db.query(Metadata).first()
        if not metadata:
            metadata = Metadata()
            db.add(metadata)
        
        # Update metadata fields
        metadata.total_questions = total_questions
        metadata.difficulty_levels = difficulty_counts
        metadata.cognitive_levels = cognitive_counts
        metadata.courses = course_counts
        metadata.covered_pages = covered_pages
        metadata.last_updated = func.now()
        
        db.commit()
        return metadata
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Error updating metadata: {str(e)}")