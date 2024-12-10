import json
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import engine
from app.models.models import Question, Metadata

def clear_existing_data(session: Session) -> None:
    """Clear existing data from tables."""
    try:
        session.execute(text('TRUNCATE TABLE questions CASCADE'))
        session.execute(text('TRUNCATE TABLE metadata CASCADE'))
        session.commit()
        print("Successfully cleared existing data")
    except Exception as e:
        print(f"Error clearing data: {str(e)}")
        session.rollback()

def load_questions(file_path: str) -> None:
    """Load questions from JSON file into database."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        questions = data['questions']
        metadata = data['metadata']

        with Session(engine) as session:
            # Clear existing data before loading new data
            clear_existing_data(session)
            
            # Generate new unique IDs for questions
            for i, q in enumerate(questions, 1):
                # Extract file number from path (e.g., 'q1.json' -> '1')
                file_num = file_path.split('/')[-1].split('.')[0].replace('q', '')
                new_id = f'Q{file_num}_{i}'
                
                # Validate page references before inserting
                if not validate_page_references(q['context_pages']):
                    print(f"Warning: Invalid page references in question {new_id}")
                    continue

                question = Question(
                    id=new_id,  # Use new unique ID
                    question_text=q['question_text'],
                    context_pages=q['context_pages'],
                    difficulty_level=q['difficulty_level'],
                    cognitive_level=q['cognitive_level'],
                    key_concepts=q['key_concepts'],
                    course_name=q['course_name'],
                    model_answer=q['model_answer'],
                    grading_criteria=q['grading_criteria']
                )
                session.add(question)

            # Load metadata
            meta = Metadata(
                total_questions=metadata['total_questions'],
                coverage_pages=metadata['coverage_pages'],
                primary_topics=metadata['primary_topics']
            )
            session.add(meta)

            try:
                session.commit()
                print(f"Successfully loaded data from {file_path}")
            except Exception as e:
                print(f"Error loading data from {file_path}: {str(e)}")
                session.rollback()


def validate_page_references(context_pages: List[int], total_pages: int = 60) -> bool:
    """Validate that referenced pages exist in the course content."""
    return all(1 <= page <= total_pages for page in context_pages)

def get_coverage_statistics(session: Session) -> Dict:
    """Calculate coverage statistics for the course content."""
    total_pages = 60
    covered_pages = set()
    
    # Get all questions and their context pages
    questions = session.query(Question).all()
    for q in questions:
        covered_pages.update(q.context_pages)
        
    coverage_percentage = (len(covered_pages) / total_pages) * 100
    uncovered_pages = set(range(1, total_pages + 1)) - covered_pages
    
    return {
        "total_pages": total_pages,
        "covered_pages": sorted(list(covered_pages)),
        "coverage_percentage": round(coverage_percentage, 2),
        "uncovered_pages": sorted(list(uncovered_pages))
    }

def get_questions_by_page(session: Session, page_number: int) -> List[Question]:
    """Get all questions that reference a specific page."""
    if not 1 <= page_number <= 60:
        raise ValueError("Invalid page number")
        
    questions = session.query(Question).all()
    return [q for q in questions if page_number in q.context_pages] 