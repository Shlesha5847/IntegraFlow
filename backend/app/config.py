from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/integraflow_db"
    identity_service_url: str = "http://localhost:8082"
    ticketing_service_url: str = "http://localhost:8083"
    legacy_hr_soap_url: str = "http://localhost:8081"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
