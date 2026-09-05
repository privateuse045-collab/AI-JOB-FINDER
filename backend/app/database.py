from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# ============================================================
# DATABASE URL
# ============================================================

DATABASE_URL = "sqlite:///./ai_job_finder_sqlalchemy.db"


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# ============================================================
# BASE CLASS
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# DATABASE SESSION
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ============================================================
# DATABASE SESSION HELPER
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()