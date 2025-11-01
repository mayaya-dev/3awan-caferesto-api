import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

db = SQLAlchemy()
#ma = Marshmallow()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
	raise ValueError("Environment variable DATABASE_URL belum diset!")

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
	"""Yield a SQLAlchemy session for use in scripts or dependency injection."""
	db_session = SessionLocal()
	try:
		yield db_session
	finally:
		db_session.close()
