from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    add_missing_sqlite_columns()


def add_missing_sqlite_columns() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    with engine.begin() as connection:
        columns = connection.execute(text("PRAGMA table_info(files)")).fetchall()
        column_names = {column[1] for column in columns}

        if "download_count" not in column_names:
            connection.execute(
                text("ALTER TABLE files ADD COLUMN download_count INTEGER NOT NULL DEFAULT 0")
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
