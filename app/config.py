import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./student_manager.db")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()
