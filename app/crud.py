from sqlalchemy.orm import Session
import models, schemas
from fastapi import HTTPException

# Participant CRUD
def create_participant(db: Session, participant: schemas.ParticipantCreate):
    db_participant = models.Participant(**participant.dict())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


def get_all_participants(db: Session):
    return db.query(models.Participant).all()


def get_participant_by_full_name(db: Session, first_name: str, last_name: str):
    return db.query(models.Participant).filter(
        models.Participant.first_name == first_name,
        models.Participant.last_name == last_name
    ).first()


# Photo CRUD
def save_photo(db: Session, photo: schemas.UploadedPhotoCreate):
    """
    Save uploaded photo details to the database.
    """
    db_photo = models.UploadedPhoto(
        first_name=photo.first_name,
        last_name=photo.last_name,
        phone_number=photo.phone_number,
        filename=photo.filename,
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


def get_all_uploaded_photos(db: Session):
    return db.query(models.UploadedPhoto).all()


# Quiz CRUD
def create_quiz(db: Session, quiz: schemas.QuizCreate):
    db_quiz = models.Quiz(**quiz.dict())
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_all_quizzes(db: Session):
    return db.query(models.Quiz).all()


# Quiz Participant CRU
def get_all_quiz_participants(db: Session):
    return db.query(models.QuizParticipant).all()

def calculate_and_save_marks(db: Session, submission: schemas.QuizSubmission):
    """
    Calculate total marks for a participant and save them to the database.
    """
    total_marks = 0
    submitted_answers = submission.answers  # {quiz_id: answer}

    # Iterate over submitted answers and calculate marks
    for quiz_id, submitted_answer in submitted_answers.items():
        quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail=f"Quiz with ID {quiz_id} not found.")
        if submitted_answer == quiz.correct_option:
            total_marks += 1

    # Save the participant's submission and total marks
    db_quiz_participant = models.QuizParticipant(
        first_name=submission.first_name,
        last_name=submission.last_name,
        phone_number=submission.phone_number,
        submitted_answers=submitted_answers,
        total_marks=total_marks,
    )
    db.add(db_quiz_participant)
    db.commit()
    db.refresh(db_quiz_participant)
    return db_quiz_participant