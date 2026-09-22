from pydantic_settings import BaseSetting

class Settings (BaseSetting):
    database_url: str = "postgresql://shelfagent:shelfagent@db:5432/shelfagent"
    s3_bucket: str = "shelfagent-snapshots"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    yolo_weights_path: str = "best.pt"
    employee_gallery_path: str = "gallery"
    # Shared secret the local camera app must send. Replace with real auth
    # (see "what's missing" at the end) before this touches a real network.
    ingest_api_key: str = "change-me"

    class Config:
        env_file = ".env"


settings = Settings()