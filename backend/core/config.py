from typing import Optional, Literal, List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn, SecretStr


class Settings(BaseSettings):
    """Application settings with environment variable override."""
    
    # App
    APP_NAME: str = "AI Job Automation"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    SECRET_KEY: SecretStr = Field(default=..., env="SECRET_KEY")
    
    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://jobuser:jobpass@localhost:5432/jobautomation",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_CACHE_TTL: int = 86400  # 24 hours
    
    # Storage (S3/R2)
    STORAGE_PROVIDER: Literal["s3", "r2"] = "s3"
    STORAGE_BUCKET: str = "job-automation"
    STORAGE_REGION: str = "us-east-1"
    STORAGE_ACCESS_KEY: Optional[str] = Field(default=None, env="STORAGE_ACCESS_KEY")
    STORAGE_SECRET_KEY: Optional[SecretStr] = Field(default=None, env="STORAGE_SECRET_KEY")
    STORAGE_ENDPOINT: Optional[str] = None  # For R2 custom endpoint
    
    # GitHub
    GITHUB_TOKEN: Optional[SecretStr] = Field(default=None, env="GITHUB_TOKEN")
    
    # AI Providers
    OPENAI_API_KEY: Optional[SecretStr] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[SecretStr] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Email
    GMAIL_CREDENTIALS_FILE: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = Field(default=None, env="SMTP_PASSWORD")
    
    # Scraping
    SCRAPE_INTERVAL_HOURS: int = 4
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RATE_LIMIT_DELAY: float = 2.0
    
    # Job Sources - LinkedIn
    LINKEDIN_ENABLED: bool = False
    LINKEDIN_EMAIL: Optional[str] = None
    LINKEDIN_PASSWORD: Optional[str] = None
    
    # Job Sources - Adzuna
    ADZUNA_ENABLED: bool = False
    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_API_KEY: Optional[str] = None
    
    # Job Sources - Remotive
    REMOTIVE_ENABLED: bool = False
    
    # Job Sources - Arbeitnow
    ARBEITNOW_ENABLED: bool = False
    
    # Job Sources - RSS
    RSS_FEEDS: List[str] = []
    
    # Scraper Settings
    SCRAPER_KEYWORDS: List[str] = []
    SCRAPER_LOCATION: Optional[str] = None
    
    # Workflow Engine
    USE_TEMPORAL: bool = False
    TEMPORAL_HOST: str = "localhost:7233"
    TEMPORAL_NAMESPACE: str = "default"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Alerts
    SLACK_WEBHOOK_URL: Optional[str] = None
    EMAIL_ALERTS_ENABLED: bool = False
    ALERTS_FROM_EMAIL: Optional[str] = None
    ALERTS_TO_EMAIL: Optional[str] = None
    
    # SMTP
    SMTP_USE_TLS: bool = True
    
    # API Key (for external services)
    API_KEY: Optional[str] = None
    SCRAPE_INTERVAL_HOURS: int = 4
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RATE_LIMIT_DELAY: float = 2.0
    
    # Rules
    DEFAULT_FILTER_RULES: dict = {
        "excluded_locations": ["remote india", "hybrid"],
        "min_salary": 80000,
        "preferred_keywords": ["python", "fastapi", "aws", "react"],
        "excluded_keywords": ["senior", "lead", "manager", "director"],
        "max_years_experience": 8
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()