from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# Example: 'mysql+pymysql://username:password@localhost/dbname'
URL_DATABASE = config("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(URL_DATABASE) # type: ignore

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your models
Base = declarative_base()

# Create all tables in the engine (will only create tables if they do not already exist)
Base.metadata.create_all(bind=engine)
