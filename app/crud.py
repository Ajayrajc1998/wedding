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


def get_participant_by_id(db: Session, participant_id: int):
    return db.query(models.Participant).filter(models.Participant.id == participant_id).first()


def update_participant(db: Session, db_participant: models.Participant, participant: schemas.ParticipantCreate):
    db_participant.first_name = participant.first_name
    db_participant.last_name = participant.last_name
    db_participant.phone_number = participant.phone_number
    db_participant.attending = participant.attending
    db.commit()
    db.refresh(db_participant)
    return db_participant


def delete_participant(db: Session, participant_id: int):
    db.query(models.Participant).filter(models.Participant.id == participant_id).delete()
    db.commit()


# Photo CRUD
def save_photo(db: Session, first_name: str, last_name: str, phone_number: str, filename: str):
    """
    Save uploaded photo details to the database.
    """
    db_photo = models.UploadedPhoto(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        filename=filename,
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


def get_all_uploaded_photos(db: Session):
    return db.query(models.UploadedPhoto).all()


def get_photo_by_id(db: Session, photo_id: int):
    return db.query(models.UploadedPhoto).filter(models.UploadedPhoto.id == photo_id).first()


def delete_photo(db: Session, photo_id: int):
    db.query(models.UploadedPhoto).filter(models.UploadedPhoto.id == photo_id).delete()
    db.commit()


# Quiz CRUD
def create_quiz(db: Session, quiz: schemas.QuizCreate):
    db_quiz = models.Quiz(**quiz.dict())
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_all_quizzes(db: Session):
    return db.query(models.Quiz).all()


def get_quiz_by_id(db: Session, quiz_id: int):
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()


def update_quiz(db: Session, db_quiz: models.Quiz, quiz: schemas.QuizCreate):
    db_quiz.question = quiz.question
    db_quiz.option_a = quiz.option_a
    db_quiz.option_b = quiz.option_b
    db_quiz.option_c = quiz.option_c
    db_quiz.option_d = quiz.option_d
    db_quiz.correct_option = quiz.correct_option
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def delete_quiz(db: Session, quiz_id: int):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if quiz:
        db.delete(quiz)
        db.commit()
    return quiz


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