import uuid
import boto3
from app.config import settings

_s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key = settings.aws_secret_access_key,
    region_name = settings.aws_region,
)

def upload_snapshot(image_bytes: bytes, content_type: str = "image/jpeg", prefix: str = "snapshots") -> str:
    """Upload an image to S3 and return its public URL. Called once for the
    raw frame and once for the annotated frame, so callers pass a prefix
    (e.g. 'snapshots' vs 'snapshots/annotated') to keep them apart."""
    key = f"{prefix}/{uuid.uuid4()}.jpg"
    _s3.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=image_bytes,
        ContentType=content_type,
    )
    return f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"

