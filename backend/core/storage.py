"""Storage management for files (S3/R2)."""

import io
from typing import Optional, BinaryIO
import aioboto3
from botocore.exceptions import ClientError

from .config import settings


class StorageManager:
    """Manage file storage in S3 or R2."""
    
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket = settings.STORAGE_BUCKET
        self.endpoint_url = settings.STORAGE_ENDPOINT
    
    async def upload_file(self, key: str, file_data: bytes, 
                          content_type: str = "application/octet-stream") -> str:
        """Upload file to storage."""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY.get_secret_value() if settings.STORAGE_SECRET_KEY else None,
            region_name=settings.STORAGE_REGION
        ) as s3:
            await s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_data,
                ContentType=content_type
            )
            
            # Generate URL
            url = f"{self.endpoint_url}/{self.bucket}/{key}" if self.endpoint_url else f"/storage/{key}"
            return url
    
    async def download_file(self, key: str) -> Optional[bytes]:
        """Download file from storage."""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY.get_secret_value() if settings.STORAGE_SECRET_KEY else None,
            region_name=settings.STORAGE_REGION
        ) as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket, Key=key)
                return await response['Body'].read()
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchKey':
                    return None
                raise
    
    async def delete_file(self, key: str) -> bool:
        """Delete file from storage."""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY.get_secret_value() if settings.STORAGE_SECRET_KEY else None,
            region_name=settings.STORAGE_REGION
        ) as s3:
            try:
                await s3.delete_object(Bucket=self.bucket, Key=key)
                return True
            except ClientError:
                return False
    
    async def file_exists(self, key: str) -> bool:
        """Check if file exists."""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY.get_secret_value() if settings.STORAGE_SECRET_KEY else None,
            region_name=settings.STORAGE_REGION
        ) as s3:
            try:
                await s3.head_object(Bucket=self.bucket, Key=key)
                return True
            except ClientError:
                return False


storage_manager = StorageManager()