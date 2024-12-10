from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class QuestionBase(BaseModel):
    question_text: str = Field(..., description="The text of the question")
    context_pages: List[int] = Field(..., description="Pages containing context for the question")
    difficulty_level: str = Field(..., description="Difficulty level of the question")
    cognitive_level: str = Field(..., description="Cognitive level of the question")
    key_concepts: List[str] = Field(..., description="Key concepts covered in the question")
    course_name: str = Field(..., description="Name of the course")
    model_answer: Dict = Field(..., description="Model answer for the question")
    grading_criteria: List[str] = Field(..., description="Criteria for grading the answer")

    model_config = {
        "from_attributes": True
    }

class QuestionCreate(QuestionBase):
    id: str = Field(..., description="Unique identifier for the question")

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    context_pages: Optional[List[int]] = None
    difficulty_level: Optional[str] = None
    cognitive_level: Optional[str] = None
    key_concepts: Optional[List[str]] = None
    course_name: Optional[str] = None
    model_answer: Optional[Dict] = None
    grading_criteria: Optional[List[str]] = None

    model_config = {
        "from_attributes": True
    }

class QuestionResponse(QuestionBase):
    id: str

    model_config = {
        "from_attributes": True
    }

class MetadataResponse(BaseModel):
    total_questions: int
    coverage_pages: List[int]
    primary_topics: List[str]

    model_config = {
        "from_attributes": True
    }