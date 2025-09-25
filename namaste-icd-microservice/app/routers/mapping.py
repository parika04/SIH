# Mapping Router - NAMASTE to ICD-11 mapping endpoints
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging

from app.services.namaste_service import NAMASTEService
from app.services.icd_service import ICDService
from app.models.icd_models import ICDMappingResponse, ICDAutocodeResponse
from app.auth.oauth2 import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
namaste_service = NAMASTEService()
icd_service = ICDService()

@router.get("/namaste-to-icd/{namaste_code}")
async def map_namaste_to_icd(
    namaste_code: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Map NAMASTE code to ICD-11 (TM2 + Biomedicine) codes
    
    - **namaste_code**: NAMASTE code to map (e.g., AYUR001, SIDD001, UNAN001)
    
    Returns both Traditional Medicine Module 2 (TM2) and Biomedicine mappings
    """
    try:
        # First lookup the NAMASTE code
        namaste_lookup = await namaste_service.lookup_code(namaste_code)
        if not namaste_lookup or not namaste_lookup.found:
            raise HTTPException(
                status_code=404, 
                detail=f"NAMASTE code '{namaste_code}' not found"
            )
        
        # Map to ICD-11
        mapping_result = await icd_service.map_namaste_to_icd(
            namaste_code, 
            namaste_lookup.term
        )
        
        return mapping_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in map_namaste_to_icd: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/translate")
async def translate_operation(
    source_system: str = Query(..., description="Source system (namaste or icd)"),
    target_system: str = Query(..., description="Target system (namaste or icd)"),
    code: str = Query(..., description="Code to translate"),
    current_user: dict = Depends(get_current_user)
):
    """
    FHIR ConceptMap $translate operation
    
    Translates codes between NAMASTE and ICD-11 systems
    
    - **source_system**: Source terminology system (namaste, icd-11-tm2, icd-11)
    - **target_system**: Target terminology system (namaste, icd-11-tm2, icd-11)
    - **code**: Code to translate
    """
    try:
        # Validate systems
        valid_systems = ["namaste", "icd-11-tm2", "icd-11"]
        if source_system not in valid_systems or target_system not in valid_systems:
            raise HTTPException(
                status_code=400,
                detail=f"Systems must be one of: {', '.join(valid_systems)}"
            )
        
        # Handle NAMASTE to ICD translation
        if source_system == "namaste" and target_system in ["icd-11-tm2", "icd-11"]:
            namaste_lookup = await namaste_service.lookup_code(code)
            if not namaste_lookup or not namaste_lookup.found:
                return {
                    "resourceType": "Parameters",
                    "parameter": [
                        {
                            "name": "result",
                            "valueBoolean": False
                        },
                        {
                            "name": "message",
                            "valueString": f"Source code '{code}' not found"
                        }
                    ]
                }
            
            # Get ICD mappings
            autocode_result = await icd_service.autocode(namaste_lookup.term)
            
            # Filter by target system
            filtered_results = []
            if target_system == "icd-11-tm2":
                filtered_results = [r for r in autocode_result.results if r.module == "tm2"]
            elif target_system == "icd-11":
                filtered_results = [r for r in autocode_result.results if r.module == "biomedicine"]
            
            if not filtered_results:
                return {
                    "resourceType": "Parameters",
                    "parameter": [
                        {
                            "name": "result",
                            "valueBoolean": False
                        },
                        {
                            "name": "message",
                            "valueString": f"No mappings found for '{code}' in {target_system}"
                        }
                    ]
                }
            
            # Return FHIR Parameters resource
            matches = []
            for result in filtered_results:
                matches.append({
                    "name": "match",
                    "part": [
                        {
                            "name": "equivalence",
                            "valueCode": "equivalent" if result.score and result.score > 0.8 else "wider"
                        },
                        {
                            "name": "concept",
                            "valueCoding": {
                                "system": f"http://id.who.int/icd/release/11/{target_system}",
                                "code": result.icd_code,
                                "display": result.title
                            }
                        }
                    ]
                })
            
            return {
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "result",
                        "valueBoolean": True
                    }
                ] + matches
            }
        
        # Handle ICD to NAMASTE translation (placeholder - would need reverse mapping)
        elif source_system in ["icd-11-tm2", "icd-11"] and target_system == "namaste":
            return {
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "result",
                        "valueBoolean": False
                    },
                    {
                        "name": "message",
                        "valueString": "ICD to NAMASTE translation not yet implemented"
                    }
                ]
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported translation direction"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in translate_operation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/autocode")
async def icd_autocode(
    term: str = Query(..., description="Term to autocode"),
    modules: str = Query("tm2+icd", description="ICD modules (tm2, icd, or tm2+icd)"),
    current_user: dict = Depends(get_current_user)
) -> ICDAutocodeResponse:
    """
    Direct ICD-11 autocode endpoint
    
    - **term**: Medical term to autocode
    - **modules**: ICD modules to search (tm2, icd, or tm2+icd)
    """
    try:
        # Parse modules parameter
        module_list = []
        if "tm2" in modules:
            module_list.append("tm2")
        if "icd" in modules:
            module_list.append("icd")
        
        if not module_list:
            raise HTTPException(
                status_code=400,
                detail="At least one module (tm2 or icd) must be specified"
            )
        
        result = await icd_service.autocode(term, module_list)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in icd_autocode: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/batch-mapping")
async def batch_namaste_mapping(
    codes: str = Query(..., description="Comma-separated NAMASTE codes"),
    limit_per_code: int = Query(3, ge=1, le=10, description="Max ICD mappings per NAMASTE code"),
    current_user: dict = Depends(get_current_user)
):
    """
    Batch mapping of multiple NAMASTE codes to ICD-11
    
    - **codes**: Comma-separated list of NAMASTE codes
    - **limit_per_code**: Maximum number of ICD mappings to return per NAMASTE code
    """
    try:
        code_list = [code.strip() for code in codes.split(",") if code.strip()]
        
        if len(code_list) > 50:  # Limit batch size
            raise HTTPException(
                status_code=400,
                detail="Maximum 50 codes allowed in batch request"
            )
        
        results = []
        
        for namaste_code in code_list:
            try:
                # Lookup NAMASTE code
                namaste_lookup = await namaste_service.lookup_code(namaste_code)
                
                if not namaste_lookup or not namaste_lookup.found:
                    results.append({
                        "namaste_code": namaste_code,
                        "found": False,
                        "error": "NAMASTE code not found"
                    })
                    continue
                
                # Get ICD mappings
                mapping_result = await icd_service.map_namaste_to_icd(
                    namaste_code, 
                    namaste_lookup.term
                )
                
                # Limit results per code
                limited_mappings = mapping_result.icd_mappings[:limit_per_code]
                
                results.append({
                    "namaste_code": namaste_code,
                    "namaste_term": namaste_lookup.term,
                    "system": namaste_lookup.system,
                    "found": True,
                    "icd_mappings": [
                        {
                            "icd_code": mapping.icd_code,
                            "title": mapping.title,
                            "module": mapping.module,
                            "score": mapping.score
                        }
                        for mapping in limited_mappings
                    ],
                    "mapping_confidence": mapping_result.mapping_confidence
                })
                
            except Exception as e:
                logger.error(f"Error mapping code {namaste_code}: {e}")
                results.append({
                    "namaste_code": namaste_code,
                    "found": False,
                    "error": "Mapping error"
                })
        
        return {
            "total_requested": len(code_list),
            "total_processed": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch_namaste_mapping: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")