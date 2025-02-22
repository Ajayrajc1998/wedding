import io
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from passlib.context import CryptContext
from typing import List
import os
from fastapi.responses import FileResponse
import logging
from fastapi.responses import StreamingResponse
from database import SessionLocal, engine
import models, schemas, crud

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

# Admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing); restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Static files directory for photos
UPLOAD_DIR = "uploaded_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Admin toggle states
admin_state = {"allow_photos": False, "allow_quiz": False}

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Admin token generation
def create_access_token(data: dict):
    """
    Creates a JWT access token without an expiration.
    """
    to_encode = data.copy()
    # Simply encode the token without adding an expiration time
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Verify admin credentials
def verify_admin(username: str, password: str):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True
    return False


# Get current admin (auth check)
def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username != ADMIN_USERNAME:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return username


@app.post("/admin/login")
def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not verify_admin(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create a token without expiration
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/admin/toggle_photos")
def toggle_photos(status: bool, admin: str = Depends(get_current_admin)):
    admin_state["allow_photos"] = status
    return {"allow_photos": admin_state["allow_photos"]}


@app.post("/admin/toggle_quiz")
def toggle_quiz(status: bool, admin: str = Depends(get_current_admin)):
    admin_state["allow_quiz"] = status
    return {"allow_quiz": admin_state["allow_quiz"]}


@app.post("/participation", response_model=schemas.Participant)
def register_participant(participant: schemas.ParticipantCreate, db: Session = Depends(get_db)):
    """
    Register a new participant with first name, last name, and attending status.
    """
    if crud.get_participant_by_full_name(db, participant.first_name, participant.last_name):
        raise HTTPException(status_code=400, detail="Participant with this name already exists.")
    return crud.create_participant(db, participant)




@app.get("/participants", response_model=List[schemas.Participant])
def get_participants(db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    return crud.get_all_participants(db)


@app.post("/upload_photo")
def upload_photo(
    first_name: str,
    last_name: str,
    phone_number: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check if photo uploads are enabled by the admin
    if not admin_state["allow_photos"]:
        raise HTTPException(status_code=403, detail="Photo uploads are disabled.")

    # Check for duplicate photo entry
    existing_photos = crud.get_photos_by_name(db, first_name, last_name)
    if any(photo.filename == file.filename for photo in existing_photos):
        raise HTTPException(status_code=400, detail="Duplicate photo entry.")

    # Ensure upload limit per participant is not exceeded
    if len(existing_photos) >= 5:
        raise HTTPException(
            status_code=400, detail=f"Photo upload limit reached for {first_name} {last_name}."
        )

    # Read the file binary data from the uploaded file
    file_data = file.file.read()

    # Save photo record in the database, including the file data
    crud.save_photo(
        db,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        filename=file.filename,
        file_data=file_data
    )
    return {
        "message": f"Photo uploaded successfully for {first_name} {last_name}.",
        "filename": file.filename,
    }


@app.get("/photos", response_model=List[schemas.UploadedPhoto])
def get_photos(db: Session = Depends(get_db)):
    # if not admin_state["allow_photos"]:
    #     raise HTTPException(status_code=403, detail="Photos are not visible.")
    return crud.get_all_uploaded_photos(db)


@app.get("/photos/{photo_id}")
def download_photo(photo_id: int, db: Session = Depends(get_db)):
    """
    Download a specific photo by photo ID by streaming the binary data stored in the database.
    """
    photo = crud.get_photo_by_id(db, photo_id)
    if not photo:
        logging.error(f"Photo with ID {photo_id} not found in the database.")
        raise HTTPException(status_code=404, detail="Photo not found.")

    # Check if binary data exists
    image_data = photo.file_data
    if not image_data:
        logging.error(f"Image data for photo ID {photo_id} is missing.")
        raise HTTPException(status_code=404, detail="File not found.")

    logging.info(f"Streaming image data for photo ID {photo_id}.")
    return StreamingResponse(io.BytesIO(image_data), media_type="image/png")


@app.delete("/upload_photo/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    """
    Delete an uploaded photo by ID.
    """
    photo = crud.get_photo_by_id(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    
    # Delete the photo file from the local storage
    filepath = os.path.join(UPLOAD_DIR, photo.filename)
    if (os.path.exists(filepath)):
        os.remove(filepath)
    
    # Delete the photo record from the database
    crud.delete_photo(db, photo_id)
    return {"message": "Photo deleted successfully"}


@app.post("/admin/quiz", response_model=schemas.Quiz)
def add_quiz(quiz: schemas.QuizCreate, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    """
    Admin creates a quiz question.
    """
    return crud.create_quiz(db, quiz)


@app.get("/quiz", response_model=List[schemas.Quiz])
def get_quiz(db: Session = Depends(get_db)):
    """
    Fetch all quiz questions (only if the admin has enabled the quiz).
    """
    # if not admin_state["allow_quiz"]:
    #     raise HTTPException(status_code=403, detail="Quiz is not available.")
    return crud.get_all_quizzes(db)

@app.post("/quiz/submit", response_model=schemas.QuizParticipant)
def submit_quiz(submission: schemas.QuizSubmission, db: Session = Depends(get_db)):
    """
    Submit all quiz answers at once and calculate total marks.
    """
    return crud.calculate_and_save_marks(db, submission)


@app.delete("/admin/quiz/{quiz_id}")
def delete_quiz(quiz_id: int, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    """
    Admin deletes a quiz question by ID.
    """
    quiz = crud.delete_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return {"message": "Quiz deleted successfully"}

@app.get("/quiz_participants", response_model=List[schemas.QuizParticipant])
def get_quiz_participants(
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),  # Admin authorization
):
    """
    Fetch the list of all quiz participants with their results.
    Admin authorization required.
    """
    return crud.get_all_quiz_participants(db)

@app.put("/participant/{participant_id}", response_model=schemas.Participant)
def update_participant(participant_id: int, participant: schemas.ParticipantCreate, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    """
    Update participant details.
    """
    db_participant = crud.get_participant_by_id(db, participant_id)
    if not db_participant:
        raise HTTPException(status_code=404, detail="Participant not found.")
    return crud.update_participant(db, db_participant, participant)


@app.put("/admin/quiz/{quiz_id}", response_model=schemas.Quiz)
def update_quiz(quiz_id: int, quiz: schemas.QuizCreate, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    """
    Update quiz details.
    """
    db_quiz = crud.get_quiz_by_id(db, quiz_id)
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return crud.update_quiz(db, db_quiz, quiz)
