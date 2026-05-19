from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class FileMetadata(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True)
    original_filename = Column(String, nullable=False, index=True)
    storage_key = Column(String, nullable=False, unique=True)
    content_type = Column(String, nullable=True, index=True)
    size_bytes = Column(Integer, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    download_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
