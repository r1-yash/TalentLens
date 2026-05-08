from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Settings
    google_api_key: str = ""
    model_name: str = "gemini-1.5-flash" # Default fallback
    embedding_model_name: str = "all-MiniLM-L6-v2"
    
    # App Settings
    app_env: str = "development"
    log_level: str = "INFO"
    
    # Security
    api_secret_key: str = "change_me"

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = Settings()
