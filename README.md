# Secure CloudVault API

I built this project to understand how cloud storage systems work internally.  
The goal was to create a small backend system where users can upload, search, list, download, and delete files while storing file metadata separately from the actual file content.

This project focuses on the backend side of a cloud storage platform: API design, metadata tracking, storage abstraction, error handling, testing, and deployment readiness.

---

## What I Built

Secure CloudVault API is a FastAPI-based cloud file storage backend with:

- File upload
- File download
- File deletion
- File listing
- Filename search
- File type filtering
- 10 MB file size validation
- Download count tracking
- SQLite metadata storage
- Local storage mode for development
- AWS S3 mode for cloud storage
- Docker support
- GitHub Actions CI
- Pytest API tests

---

## Why I Built This

Cloud storage systems do not only store files. They also need to manage:

- Metadata
- Access paths
- File size limits
- Storage keys
- Content types
- Error handling
- Search
- Monitoring-ready logs
- Reliable APIs

This project helped me understand how a backend service can separate file storage from metadata management.

---

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- AWS S3
- Boto3
- Docker
- GitHub Actions
- Pytest

---

## Project Structure

```text
secure-cloudvault-api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── storage.py
├── tests/
│   └── test_api.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Local Setup

### 1. Create virtual environment

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Mac/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create environment file

Windows CMD:

```cmd
copy .env.example .env
```

Mac/Linux:

```bash
cp .env.example .env
```

For local testing, keep this value:

```env
STORAGE_BACKEND=local
```

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Home

```http
GET /
```

### Health Check

```http
GET /health
```

### Upload File

```http
POST /files
```

### List Files

```http
GET /files
```

Optional search:

```http
GET /files?search=resume
```

Optional file type filter:

```http
GET /files?file_type=pdf
GET /files?file_type=image
GET /files?file_type=text
```

### File Metadata

```http
GET /files/{file_id}
```

### Download File

```http
GET /files/{file_id}/download
```

### Delete File

```http
DELETE /files/{file_id}
```

---

## Run with AWS S3

Update `.env`:

```env
STORAGE_BACKEND=s3
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

Then run:

```bash
uvicorn app.main:app --reload
```

---

## Docker

Build image:

```bash
docker build -t secure-cloudvault-api .
```

Run container:

```bash
docker run -p 8000:8000 --env-file .env secure-cloudvault-api
```

---

## Run Tests

```bash
pytest
```

---

## Resume Bullets

```latex
\textbf{Secure CloudVault API \textbar{} FastAPI, AWS S3, SQLite, Docker, GitHub Actions} & 2026
\begin{itemize}
  \item Built a secure cloud file storage backend supporting upload, download, search, listing, and deletion using FastAPI and AWS S3-compatible storage.
  \item Designed a metadata layer in SQLite to track filename, content type, file size, storage key, upload timestamp, version, and download count.
  \item Added file validation, error handling, local/cloud storage modes, filename search, and file-type filtering to improve API usability.
  \item Containerized the backend with Docker and configured GitHub Actions CI to run automated API tests on every push.
\end{itemize}
```

---

## Future Improvements

- Add JWT authentication
- Add user-specific file ownership
- Add PostgreSQL support
- Add file version history
- Add Terraform for AWS infrastructure
- Add CloudWatch logging
- Add presigned URL support
