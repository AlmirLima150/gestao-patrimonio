import os
from sqlmodel import create_engine, SQLModel, Session
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:projPatrimonio@db:5432/patrimonio_db")

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session