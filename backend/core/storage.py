"""Storage management for files (S3/R2) with local filesystem fallback."""

from pathlib import Path
from typing import Optional

import os
from pathlib import Path
from typing import Optional

import aioboto3
from botocore.exceptions import ClientError

from .config import settings


class StorageManager:
    """Manage file storage with S3/R2 and local filesystem fallback.

    When S3 operations fail (e.g., no credentials, network issues),
    automatically falls back to local filesystem storage.
    """

    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket = settings.STORAGE_BUCKET
        self.endpoint_url = settings.STORAGE_ENDPOINT
        self.local_path = Path(settings.LOCAL_STORAGE_PATH)

        # Ensure local storage directory exists
        self.local_path.mkdir(parents=True, exist_ok=True)

    def _s3_kwargs(self) -> dict:
        """Get common S3 client kwargs - extracted for reuse."""
        return {
            "endpoint_url": self.endpoint_url,
            "aws_access_key_id": settings.STORAGE_ACCESS_KEY,
            "aws_secret_access_key": (
                settings.STORAGE_SECRET_KEY.get_secret_value()
                if settings.STORAGE_SECRET_KEY
                else None
            ),
            "region_name": settings.STORAGE_REGION,
        }

    async def _local_upload(self, key: str, file_data: bytes) -> str:
        """Upload to local filesystem."""
        file_path = self.local_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(file_data)

        return f"/storage/{key}"

    async def _local_download(self, key: str) -> Optional[bytes]:
        """Download from local filesystem."""
        file_path = self.local_path / key
        if not file_path.exists():
            return None
        with open(file_path, "rb") as f:
            return f.read()

    async def _local_delete(self, key: str) -> bool:
        """Delete from local filesystem."""
        file_path = self.local_path / key
        try:
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception:
            return False

    async def _local_exists(self, key: str) -> bool:
        """Check if file exists in local filesystem."""
        return (self.local_path / key).exists()

    async def upload_file(
        self, key: str, file_data: bytes, content_type: str = "application/octet-stream"
    ) -> str:
        """Upload file to S3, falling back to local on failure."""
        try:
            async with self.session.client("s3", **self._s3_kwargs()) as s3:
                await s3.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=file_data,
                    ContentType=content_type,
                )
                if self.endpoint_url:
                    return f"{self.endpoint_url}/{self.bucket}/{key}"
                return f"/storage/{key}"
        except Exception:
            # Fall back to local storage
            return await self._local_upload(key, file_data)

    async def download_file(self, key: str) -> Optional[bytes]:
        """Download file from S3, falling back to local on failure."""
        try:
            async with self.session.client("s3", **self._s3_kwargs()) as s3:
                try:
                    response = await s3.get_object(Bucket=self.bucket, Key=key)
                    return await response["Body"].read()
                except ClientError as e:
                    if e.response["Error"]["Code"] == "NoSuchKey":
                        return None
                    raise
        except Exception:
            # Fall back to local storage
            return await self._local_download(key)

    async def delete_file(self, key: str) -> bool:
        """Delete file from S3, falling back to local on failure."""
        try:
            async with self.session.client("s3", **self._s3_kwargs()) as s3:
                await s3.delete_object(Bucket=self.bucket, Key=key)
                return True
        except Exception:
            # Fall back to local storage
            return await self._local_delete(key)

    async def file_exists(self, key: str) -> bool:
        """Check if file exists in S3, falling back to local on failure."""
        try:
            async with self.session.client("s3", **self._s3_kwargs()) as s3:
                await s3.head_object(Bucket=self.bucket, Key=key)
                return True
        except Exception:
            # Fall back to local storage
            return await self._local_exists(key)


storage_manager = StorageManager()
