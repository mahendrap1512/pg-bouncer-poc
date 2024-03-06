from sqlalchemy import Boolean, Column, Integer, String, create_engine

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

load_dotenv('./.env')

from constants import TaskStatus

# DB_NAME = os.environ["DB_NAME"]
# DB_USER = os.environ["DB_USER"]
# DB_PASSWORD = os.environ["DB_PASSWORD"]
# DB_HOST = os.environ["DB_HOST"]
# DB_PORT = os.environ["DB_PORT"]



DB_NAME="testdb"
DB_USER="testuser"
DB_PASSWORD="testpass"
DB_HOST="localhost"
DB_PORT=5432

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# engine = create_engine(DATABASE_URL, pool_size=300, max_overflow=100)
print("DB", DATABASE_URL)
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    status = Column(Integer, default=TaskStatus.PLANNED)

Base.metadata.create_all(bind=engine)

