from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Scholarship(Base):
    __tablename__ = 'scholarships'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    amount = Column(Float, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    target_demographics = Column(JSON, nullable=False)
    description = Column(Text, nullable=False)
    eligibility_criteria = Column(Text)
    application_requirements = Column(Text)
    deadline = Column(String(20), nullable=False, index=True)
    gpa_requirement = Column(Float, default=0.0)
    website = Column(String(500))
    contact_info = Column(String(500))
    source = Column(String(100), index=True)
    verification_status = Column(String(50), default='verified')
    application_difficulty = Column(String(20))
    estimated_applicants = Column(Integer)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    demographics = Column(JSON, default=list)
    field_of_study = Column(String(100))
    academic_level = Column(String(100))
    gpa = Column(Float, default=0.0)
    financial_need = Column(String(50))
    location = Column(String(200))
    interests = Column(JSON, default=list)
    extracurriculars = Column(JSON, default=list)
    career_goals = Column(Text)
    graduation_year = Column(Integer)
    essay_topics_interested = Column(JSON, default=list)
    application_preferences = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Application(Base):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    scholarship_id = Column(Integer, nullable=False, index=True)
    scholarship_title = Column(String(500), nullable=False)
    status = Column(String(50), default='Not Started', index=True)
    priority = Column(String(20), default='Medium')
    completion_percentage = Column(Integer, default=0)
    required_documents = Column(JSON, default=list)
    submitted_documents = Column(JSON, default=list)
    notes = Column(Text)
    reminders = Column(JSON, default=list)
    deadline = Column(DateTime)
    date_added = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SavedScholarship(Base):
    __tablename__ = 'saved_scholarships'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    scholarship_id = Column(Integer, nullable=False, index=True)
    saved_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

class SearchHistory(Base):
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    search_query = Column(String(500))
    filters_applied = Column(JSON)
    results_count = Column(Integer)
    searched_at = Column(DateTime, default=datetime.utcnow)

# Database configuration
def get_database_url():
    return os.getenv('DATABASE_URL')

def create_database_engine():
    database_url = get_database_url()
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    engine = create_engine(database_url, echo=False)
    return engine

def get_session():
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def create_tables():
    """Create all database tables"""
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all database tables (use with caution)"""
    engine = create_database_engine()
    Base.metadata.drop_all(bind=engine)