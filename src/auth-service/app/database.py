import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import URL

load_dotenv()

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("AUTH_DB_USER"),
    password=os.getenv("AUTH_DB_PASSWORD"),
    host=os.getenv("AUTH_DB_HOST"),
    port=int(os.getenv("AUTH_DB_PORT", "5432")),
    database=os.getenv("AUTH_DB_NAME")
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()