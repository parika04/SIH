# Terminology Router - NAMASTE lookup and search endpoints
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging

from app.services.namaste_service import NAMASTEService
# Note: Pydantic response models omitted due to missing definitions; returning dicts.
from app.auth.oauth2 import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize service
namaste_service = NAMASTEService()

@router.get("/lookup/{code}")
async def lookup_namaste_code(
    code: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Lookup NAMASTE code details
    
    - **code**: NAMASTE code to lookup (e.g., AYUR001, SIDD001, UNAN001)
    """
    try:
        result = await namaste_service.lookup_code(code)
        if not result:
            raise HTTPException(status_code=404, detail=f"NAMASTE code '{code}' not found")
        return result
    except Exception as e:
        logger.error(f"Error in lookup_namaste_code: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search")
async def search_namaste_terms(
    q: str = Query(..., description="Search query"),
    system: Optional[str] = Query(None, description="Filter by system (ayurveda, siddha, unani)"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    current_user: dict = Depends(get_current_user)
):
    """
    Search NAMASTE terminology
    
    - **q**: Search query string
    - **system**: Optional filter by traditional medicine system
    - **limit**: Maximum number of results (1-100)
    """
    try:
        # Validate system parameter
        if system and system not in ["ayurveda", "siddha", "unani"]:
            raise HTTPException(
                status_code=400, 
                detail="System must be one of: ayurveda, siddha, unani"
            )
        
        result = await namaste_service.search_terms(q, system, limit)
        return {"results": result, "total": len(result)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_namaste_terms: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/autocomplete")
async def autocomplete_namaste_terms(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    system: Optional[str] = Query(None, description="Filter by system"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of suggestions"),
    current_user: dict = Depends(get_current_user)
):
    """
    Autocomplete NAMASTE terms for UI widgets
    
    Returns simplified format optimized for autocomplete widgets
    """
    try:
        # Validate system parameter
        if system and system not in ["ayurveda", "siddha", "unani"]:
            raise HTTPException(
                status_code=400, 
                detail="System must be one of: ayurveda, siddha, unani"
            )
        
        search_result = await namaste_service.search_terms(q, system, limit)
        
        # Convert to autocomplete format
        suggestions = [
            {
                "code": result.get("code"),
                "term": result.get("term"),
                "system": result.get("system"),
                "display": f"{result.get('term')} ({result.get('code')}) - {str(result.get('system')).title()}"
            }
            for result in search_result
        ]
        
        return {
            "query": q,
            "suggestions": suggestions,
            "total": len(suggestions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in autocomplete_namaste_terms: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/systems")
async def get_available_systems(current_user: dict = Depends(get_current_user)):
    """Get list of available NAMASTE systems"""
    return {
        "systems": [
            {
                "code": "ayurveda",
                "name": "Ayurveda",
                "description": "Traditional Indian medicine system based on Ayurvedic principles"
            },
            {
                "code": "siddha", 
                "name": "Siddha",
                "description": "Traditional Tamil medicine system"
            },
            {
                "code": "unani",
                "name": "Unani",
                "description": "Traditional Arabic-Greek medicine system"
            }
        ]
    }

@router.get("/codes")
async def get_all_namaste_codes(
    system: Optional[str] = Query(None, description="Filter by system"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all NAMASTE codes, optionally filtered by system
    
    - **system**: Optional filter by traditional medicine system
    - **limit**: Optional limit on number of results
    """
    try:
        # Validate system parameter
        if system and system not in ["ayurveda", "siddha", "unani"]:
            raise HTTPException(
                status_code=400, 
                detail="System must be one of: ayurveda, siddha, unani"
            )
        
        codes = await namaste_service.get_all_codes(system)
        
        # Apply limit if specified
        if limit:
            codes = codes[:limit]
        
        return codes
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_all_namaste_codes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats")
async def get_namaste_statistics(current_user: dict = Depends(get_current_user)):
    """Get NAMASTE terminology statistics"""
    try:
        health = await namaste_service.health_check()
        
        if health.get("status") != "healthy":
            raise HTTPException(status_code=503, detail="NAMASTE service unhealthy")
        
        return {
            "total_codes": health.get("count"),
            "systems": ["ayurveda", "siddha", "unani"],
            "loaded_at": health.get("loaded_at"),
            "status": health.get("status")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_namaste_statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")