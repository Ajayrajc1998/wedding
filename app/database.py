from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Create the SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Create a configured "Session" class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Base class for our models
    Base = declarative_base()
except Exception as e:
    print(f"database URL: {DATABASE_URL}")
    print(f"Error: {e}")