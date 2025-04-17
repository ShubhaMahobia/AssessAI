from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
import json
from typing import Dict, Any, List, Optional
import uuid

# Create the SQLAlchemy base
Base = declarative_base()

class Candidate(Base):
    """Model for storing candidate information with GDPR considerations."""
    
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(String(36), unique=True, nullable=False)  # UUID for external reference
    
    # Personal data (can be encrypted in production)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    
    # Professional information
    experience_years = Column(String(10), nullable=True)
    desired_position = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    tech_stack = Column(String(255), nullable=True)
    
    # GDPR compliance fields
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime, nullable=True)
    data_retention_period = Column(Integer, default=365)  # Days to retain data
    anonymize_after = Column(DateTime, nullable=True)
    
    # Interview metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationship with interview responses
    responses = relationship("InterviewResponse", back_populates="candidate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Candidate(id={self.candidate_id}, name='{self.name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary."""
        return {
            "candidate_id": self.candidate_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "experience_years": self.experience_years,
            "desired_position": self.desired_position,
            "location": self.location,
            "tech_stack": self.tech_stack,
            "consent_given": self.consent_given,
            "consent_timestamp": self.consent_timestamp.isoformat() if self.consent_timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def anonymize(self) -> None:
        """Anonymize personal data for GDPR compliance."""
        self.name = f"Anonymized User {self.id}"
        self.email = f"anonymized{self.id}@example.com"
        self.phone = "0000000000"
        # Keep non-identifying information for analytics

class InterviewResponse(Base):
    """Model for storing interview Q&A."""
    
    __tablename__ = 'interview_responses'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    
    # Interview data
    technology = Column(String(50), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with candidate
    candidate = relationship("Candidate", back_populates="responses")
    
    def __repr__(self):
        return f"<InterviewResponse(id={self.id}, technology='{self.technology}')>"


class DatabaseManager:
    """Manager for database operations with GDPR compliance."""
    
    def __init__(self, db_path: str = "sqlite:///interviews.db"):
        """Initialize the database manager.
        
        Args:
            db_path: Database connection string
        """
        self.engine = create_engine(db_path)
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
    
    def create_candidate(self, candidate_data: Dict[str, Any], consent_given: bool = False) -> str:
        """Create a new candidate record.
        
        Args:
            candidate_data: Candidate information
            consent_given: Whether the candidate gave GDPR consent
            
        Returns:
            Candidate ID
        """
        session = self.Session()
        try:
            # Generate unique candidate ID
            candidate_id = str(uuid.uuid4())
            
            # Create retention date (default 1 year)
            anonymize_after = datetime.utcnow().replace(year=datetime.utcnow().year + 1)
            
            # Create candidate record
            candidate = Candidate(
                candidate_id=candidate_id,
                name=candidate_data.get('name', ''),
                email=candidate_data.get('email', ''),
                phone=candidate_data.get('phone', ''),
                experience_years=candidate_data.get('experience', ''),
                desired_position=candidate_data.get('position', ''),
                location=candidate_data.get('location', ''),
                tech_stack=candidate_data.get('tech_stack', ''),
                consent_given=consent_given,
                consent_timestamp=datetime.utcnow() if consent_given else None,
                anonymize_after=anonymize_after
            )
            
            session.add(candidate)
            session.commit()
            return candidate_id
        finally:
            session.close()
    
    def store_interview_responses(self, candidate_id: str, responses: Dict[str, List[Dict[str, str]]]) -> None:
        """Store interview responses.
        
        Args:
            candidate_id: Unique candidate ID
            responses: Dictionary of technology -> list of question/answer pairs
        """
        session = self.Session()
        try:
            # Get candidate record
            candidate = session.query(Candidate).filter_by(candidate_id=candidate_id).first()
            
            if not candidate:
                raise ValueError(f"Candidate with ID {candidate_id} not found")
            
            # Store each response
            for tech, qa_list in responses.items():
                for qa_pair in qa_list:
                    response = InterviewResponse(
                        candidate_id=candidate.id,
                        technology=tech,
                        question=qa_pair.get('question', ''),
                        answer=qa_pair.get('answer', '')
                    )
                    session.add(response)
            
            session.commit()
        finally:
            session.close()
    
    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get candidate information.
        
        Args:
            candidate_id: Unique candidate ID
            
        Returns:
            Candidate data or None if not found
        """
        session = self.Session()
        try:
            candidate = session.query(Candidate).filter_by(candidate_id=candidate_id).first()
            if candidate:
                return candidate.to_dict()
            return None
        finally:
            session.close()
    
    def update_consent(self, candidate_id: str, consent_given: bool) -> bool:
        """Update GDPR consent status.
        
        Args:
            candidate_id: Unique candidate ID
            consent_given: Whether consent is given
            
        Returns:
            Success status
        """
        session = self.Session()
        try:
            candidate = session.query(Candidate).filter_by(candidate_id=candidate_id).first()
            if not candidate:
                return False
            
            candidate.consent_given = consent_given
            candidate.consent_timestamp = datetime.utcnow() if consent_given else None
            
            session.commit()
            return True
        finally:
            session.close()
    
    def anonymize_expired_data(self) -> int:
        """Anonymize data that has passed retention period.
        
        Returns:
            Number of records anonymized
        """
        session = self.Session()
        try:
            now = datetime.utcnow()
            expired = session.query(Candidate).filter(Candidate.anonymize_after <= now).all()
            
            for candidate in expired:
                candidate.anonymize()
            
            count = len(expired)
            session.commit()
            return count
        finally:
            session.close()
    
    def delete_candidate_data(self, candidate_id: str) -> bool:
        """Delete candidate data (right to be forgotten).
        
        Args:
            candidate_id: Unique candidate ID
            
        Returns:
            Success status
        """
        session = self.Session()
        try:
            candidate = session.query(Candidate).filter_by(candidate_id=candidate_id).first()
            if not candidate:
                return False
            
            session.delete(candidate)  # Will cascade delete responses
            session.commit()
            return True
        finally:
            session.close() 