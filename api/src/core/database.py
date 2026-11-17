# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# ⚠️ Adapter l'URL selon ta DB réelle (voir question en bas)
# SQLite :
DATABASE_URL = "sqlite:///./event_management.db"
# MySQL (exemple) :
# DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/event_management"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
