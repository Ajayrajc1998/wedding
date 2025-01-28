from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict


class ParticipantBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    attending: bool  # Boolean for attending status


class ParticipantCreate(ParticipantBase):
    pass


class Participant(ParticipantBase):
    id: int

    class Config:
        orm_mode = True


class UploadedPhotoBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    filename: str


class UploadedPhotoCreate(UploadedPhotoBase):
    pass


class UploadedPhoto(UploadedPhotoBase):
    id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True


class QuizBase(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str


class QuizCreate(QuizBase):
    pass


class Quiz(QuizBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class QuizSubmission(BaseModel):
    """
    Schema for submitting all quiz answers at once.
    """
    first_name: str
    last_name: str
    phone_number: str
    answers: Dict[int, str]  # A dictionary of {quiz_id: answer}


class QuizParticipant(BaseModel):
    """
    Schema for storing the final quiz result for a participant.
    """
    id: int
    first_name: str
    last_name: str
    phone_number: str
    submitted_answers: Dict[int, str]  # Submitted answers in {quiz_id: answer} format
    total_marks: int  # Total marks obtained by the participant
    submitted_at: datetime

    class Config:
        orm_mode = True
