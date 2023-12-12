from fastapi import HTTPException
import boto3
from config import settings


class S3Service:
    def __init__(self) -> None:
        self.key = settings.AWS_ACCESS_KEY
        self.secret = settings.AWS_SECRET_KEY
        self.s3 = boto3.client(
            "s3", aws_access_key_id=self.key, aws_secret_access_key=self.secret
        )
        self.bucket = settings.AWS_BUCKET_NAME
        self.region = settings.AWS_REGION

    def upload(self, path, key, ext):
        try:
            self.s3.upload_photo(
                path,
                self.bucket,
                key,
                ExtraArgs={"ACL": "public-read", "ContentType": f"image/{ext}"},
            )
            return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
        except Exception:
            raise HTTPException(500, "S3 is not available")
