# app/config.py

import os
from typing import Optional


class Settings:
    def __init__(self):
        # Application
        self.app_name: str = self._get_env("APP_NAME", "NAMASTE-ICD-11 Terminology Microservice")
        self.version: str = self._get_env("VERSION", "1.0.0")
        self.debug: bool = self._get_env_bool("DEBUG", False)

        # WHO ICD-11 API
        self.icd_client_id: str = self._get_env("ICD_CLIENT_ID", "")
        self.icd_client_secret: str = self._get_env("ICD_CLIENT_SECRET", "")
        self.icd_api_base: str = self._get_env("ICD_API_BASE", "https://id.who.int/icd/release/11")
        self.icd_auth_url: str = self._get_env("ICD_AUTH_URL", "https://id.who.int/icd/api/token")

        # ABHA / OAuth2
        self.abha_base_url: str = self._get_env("ABHA_BASE_URL", "https://sandbox.abdm.gov.in")
        self.abha_session_url: str = self._get_env("ABHA_SESSION_URL", "https://sandbox.abdm.gov.in/api/v1/session")
        self.abha_verify_url: str = self._get_env("ABHA_VERIFY_URL", "https://sandbox.abdm.gov.in/api/v1/auth/verify")
        self.abha_client_id: str = self._get_env("ABHA_CLIENT_ID", "")
        self.abha_client_secret: str = self._get_env("ABHA_CLIENT_SECRET", "")

        # Database
        self.database_url: str = self._get_env("DATABASE_URL", "sqlite:///./local.db")

        # FHIR
        self.fhir_base_url: str = self._get_env("FHIR_BASE_URL", "http://localhost:8000")
        self.fhir_version: str = self._get_env("FHIR_VERSION", "4.0.1")

        # Audit
        self.enable_audit: bool = self._get_env_bool("ENABLE_AUDIT", True)
        self.audit_retention_days: int = self._get_env_int("AUDIT_RETENTION_DAYS", 365)

        # Optional extras
        self.log_level: str = self._get_env("LOG_LEVEL", "info")
        self.rate_limit_requests_per_minute: int = self._get_env_int("RATE_LIMIT_REQUESTS_PER_MINUTE", 100)

        # Data file paths
        self.ayurveda_csv: str = self._get_env("AYURVEDA_CSV", "data/ayurveda.csv")
        self.siddha_csv: str = self._get_env("SIDDHA_CSV", "data/siddha.csv")
        self.unani_csv: str = self._get_env("UNANI_CSV", "data/unani.csv")

        # Output
        self.output_dir: str = self._get_env("OUTPUT_DIR", "output")
        self.fhir_resources_dir: str = self._get_env("FHIR_RESOURCES_DIR", "output")

        # JWT / OAuth configuration for local issuance
        self.jwt_secret_key: str = self._get_env("JWT_SECRET_KEY", "dev-secret-change-me")
        self.jwt_algorithm: str = self._get_env("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = self._get_env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 60)

    def _get_env(self, key: str, default: str) -> str:
        """Get environment variable with default value"""
        return os.getenv(key, default)

    def _get_env_bool(self, key: str, default: bool) -> bool:
        """Get environment variable as boolean"""
        value = os.getenv(key, "").lower()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off"):
            return False
        return default

    def _get_env_int(self, key: str, default: int) -> int:
        """Get environment variable as integer"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default


# Instantiate for import
settings = Settings()
