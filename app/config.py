"""Application settings loaded from the environment."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration required to connect to the application database."""

    DATABASE_URL: str = "postgresql+psycopg://csd:csd@localhost:5432/csd"


# def load_settings() -> Settings:
#     """Load required settings and fail before connecting to the wrong database"""
#     database_url = os.environ.get("DATABASE_URL")

#     if not database_url:
#         raise RuntimeError("DATABASE_URL must be set.")

#     return Settings(DATABASE_URL=database_url)

settings = Settings()
