# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "NAMASTE-ICD-11 Terminology Microservice"
    version: str = "1.0.0"
    debug: bool = False

    # WHO ICD-11 API
    icd_client_id: str = ""
    icd_client_secret: str = ""
    icd_api_base: str = "https://id.who.int/icd/release/11"
    icd_auth_url: str = "https://id.who.int/icd/api/token"

    # ABHA / OAuth2
    abha_base_url: str = "https://sandbox.abdm.gov.in"
    abha_session_url: str = "https://sandbox.abdm.gov.in/api/v1/session"
    abha_verify_url: str = "https://sandbox.abdm.gov.in/api/v1/auth/verify"
    abha_client_id: str = ""
    abha_client_secret: str = ""

    # Database
    database_url: str = "sqlite:///./local.db"

    # FHIR
    fhir_base_url: str = "http://localhost:8000"
    fhir_version: str = "4.0.1"

    # Audit
    enable_audit: bool = True
    audit_retention_days: int = 365

    # Optional extras
    log_level: str = "info"
    rate_limit_requests_per_minute: int = 100

    # Data file paths
    ayurveda_csv: str = "data/ayurveda.csv"
    siddha_csv: str = "data/siddha.csv"
    unani_csv: str = "data/unani.csv"

    # Output
    output_dir: str = "output"
    fhir_resources_dir: str = "output"

    # JWT / OAuth configuration for local issuance
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # pydantic-settings v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


# Instantiate for import
settings = Settings()
