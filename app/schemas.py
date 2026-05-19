from datetime import datetime
from pydantic import BaseModel


class FileResponse(BaseModel):
    id: str
    original_filename: str
    content_type: str | None
    size_bytes: int
    version: int
    download_count: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class MessageResponse(BaseModel):
    message: str
