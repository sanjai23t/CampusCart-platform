
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker


# PostgreSQL database connection URL
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("CART_DB_USER"),
    password=os.getenv("CART_DB_PASSWORD"),
    host=os.getenv("CART_DB_HOST"),
    port=int(os.getenv("CART_DB_PORT", "5432")),
    database=os.getenv("CART_DB_NAME")
)


# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for SQLAlchemy models
Base = declarative_base()
