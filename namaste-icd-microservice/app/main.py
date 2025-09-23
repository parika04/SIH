# Main FastAPI Application
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from datetime import datetime

from app.config import settings
from app.auth.oauth2 import get_current_user
from app.routers import terminology, mapping, fhir
from app.services.audit_service import AuditService
from app.services.namaste_service import NAMASTEService
from app.services.icd_service import ICDService
from app.services.fhir_service import FHIRService

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="FHIR R4-compliant terminology microservice for NAMASTE-ICD-11 integration",
    version=settings.version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
audit_service = AuditService()
namaste_service = NAMASTEService()
icd_service = ICDService()
fhir_service = FHIRService()

# Include routers with authentication
app.include_router(
    terminology.router, 
    prefix="/api/v1/terminology",
    tags=["Terminology"],
    dependencies=[Depends(get_current_user)] if not settings.debug else []
)

app.include_router(
    mapping.router, 
    prefix="/api/v1/mapping",
    tags=["Mapping"],
    dependencies=[Depends(get_current_user)] if not settings.debug else []
)

app.include_router(
    fhir.router, 
    prefix="/api/v1/fhir",
    tags=["FHIR Resources"],
    dependencies=[Depends(get_current_user)] if not settings.debug else []
)

# NOTE: Bundle ingestion router not yet implemented. Remove include to avoid import error.

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting NAMASTE-ICD-11 Terminology Microservice")
    
    # Load NAMASTE data
    try:
        await namaste_service.load_data()
        logger.info("NAMASTE data loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load NAMASTE data: {e}")
    
    # Initialize FHIR resources
    try:
        await fhir_service.initialize_resources()
        logger.info("FHIR resources initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize FHIR resources: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NAMASTE ↔ ICD-11 Terminology Microservice",
        "version": settings.version,
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "terminology": "/api/v1/terminology",
            "mapping": "/api/v1/mapping", 
            "fhir": "/api/v1/fhir",
            "bundles": "/api/v1/bundle",
            "docs": "/docs" if settings.debug else "disabled"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.version,
        "services": {
            "namaste": await namaste_service.health_check(),
            "icd": await icd_service.health_check(),
            "fhir": await fhir_service.health_check()
        }
    }

@app.get("/metadata")
async def capability_statement():
    """FHIR CapabilityStatement endpoint"""
    return await fhir_service.get_capability_statement()

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with audit logging"""
    if settings.enable_audit:
        await audit_service.log_error(
            request=request,
            error=exc,
            timestamp=datetime.now().isoformat()
        )
    
    return {
        "error": {
            "code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )