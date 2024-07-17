from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from service.App import App

try:
    SQLALCHEMY_DATABASE_URL = App.config["SQLALCHEMY_DATABASE_URI"]
except KeyError:
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"  # Default to in-memory SQLite database

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
