from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey,JSON
from database import Base
from datetime import datetime

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)  # First name of the participant
    last_name = Column(String, nullable=False)  # Last name of the participant
    phone_number = Column(String, unique=True, nullable=False)  # Phone number must be unique
    attending = Column(Boolean, nullable=False)  # Boolean for attending status



class QuizParticipant(Base):
    __tablename__ = "quiz_participants"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)  # First name of the participant
    last_name = Column(String, nullable=False)   # Last name of the participant
    phone_number = Column(String, nullable=False)  # Phone number of the participant
    submitted_answers = Column(JSON, nullable=False)  # Submitted answers in JSON format
    total_marks = Column(Integer, default=0)  # Total marks for the participant
    submitted_at = Column(DateTime, default=datetime.utcnow)  # Submission timestamp


class Quiz(Base):
    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_option = Column(String, nullable=False)  # E.g., 'A', 'B', 'C', or 'D'
    created_at = Column(DateTime, default=datetime.utcnow)

class UploadedPhoto(Base):
    __tablename__ = "uploaded_photos"

    id = Column(Integer, primary_key=True, index=True)  # Primary key
    first_name = Column(String, nullable=False)  # First name of the uploader
    last_name = Column(String, nullable=False)  # Last name of the uploader
    phone_number = Column(String, nullable=False)  # Phone number of the uploader
    filename = Column(String, unique=True, nullable=False)  # File name of the uploaded photo
    uploaded_at = Column(DateTime, default=datetime.utcnow)  # Timestamp when the photo was uploaded


