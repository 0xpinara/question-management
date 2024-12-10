from sqlalchemy import Column, Integer, String, JSON, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config.database import Base
import enum

class DifficultyLevel(str, enum.Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class CognitiveLevel(str, enum.Enum):
    KNOWLEDGE = "knowledge"
    COMPREHENSION = "comprehension"
    APPLICATION = "application"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    EVALUATION = "evaluation"

class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True)
    question_text = Column(Text, nullable=False)
    context_pages = Column(JSON, nullable=False)  # Store as JSON array
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    cognitive_level = Column(Enum(CognitiveLevel), nullable=False)
    key_concepts = Column(JSON, nullable=False)  # Store as JSON array
    course_name = Column(String, nullable=False)
    model_answer = Column(JSON, nullable=False)  # Store as JSON object
    grading_criteria = Column(JSON, nullable=False)  # Store as JSON array

class Metadata(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True)
    total_questions = Column(Integer, nullable=False)
    coverage_pages = Column(JSON, nullable=False)  # Store as JSON array
    primary_topics = Column(JSON, nullable=False)  # Store as JSON array