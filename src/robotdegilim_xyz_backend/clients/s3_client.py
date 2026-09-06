import json
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from robotdegilim_xyz_backend.core.config import get_settings
from robotdegilim_xyz_backend.core.exceptions import AppException

logger = logging.getLogger(__name__)

class S3Client:
    """
    A generic AWS S3 client wrapper for managing queue, lock, and state files.
    """
    def __init__(self):
        settings = get_settings()
        self.bucket = settings.S3_BUCKET
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        )

    def upload_json(self, key: str, payload: dict | None = None, public_read: bool = False) -> None:
        if payload is None:
            payload = {}
            
        json_data = json.dumps(payload).encode('utf-8')
        
        kwargs = {
            'Bucket': self.bucket,
            'Key': key,
            'Body': json_data,
            'ContentType': 'application/json'
        }
        
        if public_read:
            kwargs['ACL'] = 'public-read'
            
        try:
            self.client.put_object(**kwargs)
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"S3 Upload failed for key {key}: {e}")
            raise AppException("Failed to communicate with the storage service.", status_code=503)

    def download_json(self, key: str) -> dict:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise AppException(f"Key {key} not found", status_code=404)
            logger.error(f"S3 Download failed for key {key}: {e}")
            raise AppException("Failed to communicate with the storage service.", status_code=503)

    def list_files(self, prefix: str) -> list[dict]:
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            
            if 'Contents' not in response:
                return []
                
            return [
                {
                    "key": item["Key"],
                    "last_modified": item["LastModified"]
                }
                for item in response["Contents"]
            ]
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"S3 List failed for prefix {prefix}: {e}")
            raise AppException("Failed to communicate with the storage service.", status_code=503)

    def delete(self, key: str | None = None, prefix: str | None = None) -> None:
        try:
            if key:
                self.client.delete_object(Bucket=self.bucket, Key=key)
            elif prefix:
                files = self.list_files(prefix)
                if not files:
                    return
                objects_to_delete = [{'Key': f['key']} for f in files]
                self.client.delete_objects(
                    Bucket=self.bucket,
                    Delete={'Objects': objects_to_delete}
                )
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"S3 Delete failed: {e}")
            raise AppException("Failed to modify storage state.", status_code=503)

    def file_exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"S3 Head Object failed for key {key}: {e}")
            raise AppException("Failed to check storage state.", status_code=503)

s3_client = S3Client()
