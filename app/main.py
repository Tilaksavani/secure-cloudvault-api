import io
import uuid

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import create_tables, get_db
from app.models import FileMetadata
from app.schemas import FileResponse, MessageResponse
from app.storage import StorageError, get_storage

app = FastAPI(
    title="Secure CloudVault API",
    description="A FastAPI backend for cloud-style file storage with metadata tracking, search, filtering, and local/AWS storage modes.",
    version="1.1.0",
)


@app.on_event("startup")
def startup_event() -> None:
    create_tables()


@app.get("/")
def home() -> dict:
    return {
        "message": "Secure CloudVault API is running",
        "docs": "/docs",
        "health": "/health",
        "max_file_size_mb": settings.max_file_size_mb,
    }


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/files", response_model=FileResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    content = await file.read()
    size_bytes = len(content)

    if size_bytes == 0:
        raise HTTPException(status_code=400, detail="Empty files are not allowed")

    max_size_bytes = settings.max_file_size_mb * 1024 * 1024
    if size_bytes > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {settings.max_file_size_mb} MB",
        )

    file_id = str(uuid.uuid4())
    storage_key = f"uploads/{file_id}_{file.filename}"

    try:
        storage = get_storage()
        storage.upload(
            file_obj=io.BytesIO(content),
            key=storage_key,
            content_type=file.content_type,
        )
    except StorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    metadata = FileMetadata(
        id=file_id,
        original_filename=file.filename,
        storage_key=storage_key,
        content_type=file.content_type,
        size_bytes=size_bytes,
        version=1,
        download_count=0,
    )

    db.add(metadata)
    db.commit()
    db.refresh(metadata)

    return metadata


@app.get("/files", response_model=list[FileResponse])
def list_files(
    search: str | None = Query(default=None, description="Search files by filename"),
    file_type: str | None = Query(default=None, description="Filter by file type: pdf, image, text, csv, json"),
    db: Session = Depends(get_db),
):
    query = db.query(FileMetadata)

    if search:
        query = query.filter(FileMetadata.original_filename.ilike(f"%{search}%"))

    if file_type:
        file_type = file_type.lower()

        type_map = {
            "pdf": "application/pdf",
            "image": "image/",
            "text": "text/",
            "csv": "csv",
            "json": "json",
        }

        pattern = type_map.get(file_type, file_type)

        if pattern.endswith("/"):
            query = query.filter(FileMetadata.content_type.ilike(f"{pattern}%"))
        else:
            query = query.filter(FileMetadata.content_type.ilike(f"%{pattern}%"))

    return query.order_by(FileMetadata.created_at.desc()).all()


@app.get("/files/{file_id}", response_model=FileResponse)
def get_file_metadata(file_id: str, db: Session = Depends(get_db)):
    metadata = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()

    if metadata is None:
        raise HTTPException(status_code=404, detail="File metadata not found")

    return metadata


@app.get("/files/{file_id}/download")
def download_file(file_id: str, db: Session = Depends(get_db)):
    metadata = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()

    if metadata is None:
        raise HTTPException(status_code=404, detail="File metadata not found")

    try:
        storage = get_storage()
        data = storage.download(metadata.storage_key)
    except StorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    metadata.download_count += 1
    db.commit()

    headers = {
        "Content-Disposition": f'attachment; filename="{metadata.original_filename}"'
    }

    return Response(
        content=data,
        media_type=metadata.content_type or "application/octet-stream",
        headers=headers,
    )


@app.delete("/files/{file_id}", response_model=MessageResponse)
def delete_file(file_id: str, db: Session = Depends(get_db)):
    metadata = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()

    if metadata is None:
        raise HTTPException(status_code=404, detail="File metadata not found")

    try:
        storage = get_storage()
        storage.delete(metadata.storage_key)
    except StorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    db.delete(metadata)
    db.commit()

    return {"message": "File deleted successfully"}
