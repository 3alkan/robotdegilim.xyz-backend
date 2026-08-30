import json
import boto3
from botocore.exceptions import ClientError

from robotdegilim_xyz_backend.core.config import get_settings

class S3Client:
    """
    A generic AWS S3 client wrapper for managing queue, lock, and state files.
    This class hides the raw boto3 logic from the rest of the application.
    """
    def __init__(self):
        settings = get_settings()
        self.bucket = settings.S3_BUCKET
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            # region_name="us-east-1" # Add if your bucket requires a specific region
        )

    def upload_json(self, key: str, payload: dict | None = None) -> None:
        """
        Uploads a dictionary as a JSON file to the specified key.
        If no payload is provided, uploads an empty JSON object '{}'.
        """
        if payload is None:
            payload = {}
            
        json_data = json.dumps(payload).encode('utf-8')
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json_data,
            ContentType='application/json'
        )

    def list_files(self, prefix: str) -> list[dict]:
        """
        Returns a list of files matching the prefix.
        Each item is a dict containing the 'key' and 'last_modified' timestamp.
        """
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

    def delete(self, key: str | None = None, prefix: str | None = None) -> None:
        """
        Deletes files from S3.
        Provide 'key' to delete a single exact file.
        Provide 'prefix' to bulk-delete all files matching the prefix.
        """
        if key:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            
        elif prefix:
            files = self.list_files(prefix)
            if not files:
                return
                
            # S3 bulk delete format requires a specific dictionary structure
            objects_to_delete = [{'Key': f['key']} for f in files]
            self.client.delete_objects(
                Bucket=self.bucket,
                Delete={'Objects': objects_to_delete}
            )

    def file_exists(self, key: str) -> bool:
        """
        Quickly checks if a specific exact file exists using a Head request.
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise # Re-raise if it's a real error (like permission denied)

# Export a single instance to be used across the app
s3_client = S3Client()
