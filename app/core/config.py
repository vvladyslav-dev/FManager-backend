from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Azure Blob Storage
    azure_storage_connection_string: str
    azure_storage_container_name: str = "forms-files"
    
    # Application
    app_name: str = "Form Manager API"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()  # type: ignore

