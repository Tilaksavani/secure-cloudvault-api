from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings


class StorageError(Exception):
    pass


class BaseStorage:
    def upload(self, file_obj: BinaryIO, key: str, content_type: str | None) -> None:
        raise NotImplementedError

    def download(self, key: str) -> bytes:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError


class LocalStorage(BaseStorage):
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe_key = key.replace("/", "_")
        return self.base_dir / safe_key

    def upload(self, file_obj: BinaryIO, key: str, content_type: str | None) -> None:
        path = self._path(key)
        with path.open("wb") as output:
            output.write(file_obj.read())

    def download(self, key: str) -> bytes:
        path = self._path(key)
        if not path.exists():
            raise StorageError("File not found in local storage")
        return path.read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()


class S3Storage(BaseStorage):
    def __init__(self):
        if not settings.aws_s3_bucket:
            raise StorageError("AWS_S3_BUCKET is required when STORAGE_BACKEND=s3")

        self.bucket = settings.aws_s3_bucket
        self.client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )

    def upload(self, file_obj: BinaryIO, key: str, content_type: str | None) -> None:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        try:
            self.client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket,
                Key=key,
                ExtraArgs=extra_args,
            )
        except (BotoCoreError, ClientError) as exc:
            raise StorageError(f"S3 upload failed: {exc}") from exc

    def download(self, key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except (BotoCoreError, ClientError) as exc:
            raise StorageError(f"S3 download failed: {exc}") from exc

    def delete(self, key: str) -> None:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except (BotoCoreError, ClientError) as exc:
            raise StorageError(f"S3 delete failed: {exc}") from exc


def get_storage() -> BaseStorage:
    backend = settings.storage_backend.lower()

    if backend == "s3":
        return S3Storage()

    if backend == "local":
        return LocalStorage(settings.local_storage_dir)

    raise StorageError("Unsupported STORAGE_BACKEND. Use 'local' or 's3'.")
