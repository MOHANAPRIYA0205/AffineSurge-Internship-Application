from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str
    DATABASE_URL: str
    MONGO_URI: str
    ANTHROPIC_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env.example", env_file_encoding="utf-8")

settings = Settings()
