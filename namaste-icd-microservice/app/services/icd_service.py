# ICD-11 Service - WHO ICD API integration
import httpx
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import base64
import json

from app.config import settings
from app.models.icd_models import (
    ICDCode, ICDAutocodeResponse, ICDAutocodeResult, ICDMappingResponse
)

logger = logging.getLogger(__name__)

class ICDService:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.client_id = settings.icd_client_id
        self.client_secret = settings.icd_client_secret
        self.api_base = settings.icd_api_base
        self.auth_url = settings.icd_auth_url

    async def get_access_token(self) -> str:
        """Get or refresh WHO ICD API access token"""
        
        # Check if current token is still valid
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        try:
            # Prepare authentication
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('utf-8')
            auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "client_credentials",
                "scope": "icdapi_access"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.auth_url, headers=headers, data=data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    
                    logger.info("Successfully obtained ICD API access token")
                    return self.access_token
                else:
                    logger.error(f"Failed to get ICD API token: {response.status_code} - {response.text}")
                    raise Exception(f"ICD API authentication failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting ICD API access token: {e}")
            raise

    async def autocode(self, term: str, modules: List[str] = ["tm2", "icd"]) -> ICDAutocodeResponse:
        """Autocode a term using WHO ICD-11 API"""
        
        try:
            token = await self.get_access_token()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "API-Version": "v2",
                "Accept-Language": "en"
            }
            
            # Prepare modules parameter
            modules_param = "+".join(modules)
            
            params = {
                "searchText": term.strip(),
                "subtreeFilterUsesFoundationDescendants": "false",
                "includeKeywordResult": "false",
                "useFlexisearch": "false",
                "flatResults": "false",
                "highlightingEnabled": "false",
                "medicalCodingMode": "true",
                "chapterFilter": "",
                "linearizationname": modules_param
            }
            
            url = f"{self.api_base}/autocode"
            
            logger.debug(f"ICD Autocode request: {url} with params: {params}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                
                logger.debug(f"ICD Autocode response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"ICD Autocode response data: {json.dumps(data, indent=2)}")
                    
                    results = []
                    
                    # Parse destinationEntities from response
                    if "destinationEntities" in data and data["destinationEntities"]:
                        for entity in data["destinationEntities"]:
                            # Determine module based on theCode
                            module = "biomedicine"  # default
                            if "TM" in entity.get("theCode", ""):
                                module = "tm2"
                            elif "Chapter" in entity.get("chapter", ""):
                                if "Traditional Medicine" in entity.get("chapter", ""):
                                    module = "tm2"
                            
                            result = ICDAutocodeResult(
                                icd_code=entity.get("theCode", ""),
                                title=entity.get("title", ""),
                                module=module,
                                score=entity.get("score", 0.0)
                            )
                            results.append(result)
                    
                    # Also check matchingEntities for additional results
                    if "matchingEntities" in data and data["matchingEntities"]:
                        for entity in data["matchingEntities"]:
                            module = "biomedicine"
                            if "TM" in entity.get("theCode", ""):
                                module = "tm2"
                                
                            result = ICDAutocodeResult(
                                icd_code=entity.get("theCode", ""),
                                title=entity.get("title", ""),
                                module=module,
                                score=entity.get("score", 0.0)
                            )
                            results.append(result)
                    
                    return ICDAutocodeResponse(
                        term=term,
                        results=results,
                        total=len(results)
                    )
                    
                else:
                    logger.error(f"ICD Autocode API error: {response.status_code} - {response.text}")
                    return ICDAutocodeResponse(term=term, results=[], total=0)
                    
        except Exception as e:
            logger.error(f"Error in ICD autocode for term '{term}': {e}")
            return ICDAutocodeResponse(term=term, results=[], total=0)

    async def lookup_code(self, code: str) -> Optional[ICDCode]:
        """Lookup specific ICD-11 code details"""
        
        try:
            token = await self.get_access_token()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "API-Version": "v2",
                "Accept-Language": "en"
            }
            
            # Clean the code (remove any URL encoding)
            clean_code = code.replace("%2F", "/")
            url = f"{self.api_base}/entity/{clean_code}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Determine module
                    module = "biomedicine"
                    if "TM" in code or "Traditional Medicine" in data.get("chapter", {}).get("title", ""):
                        module = "tm2"
                    
                    return ICDCode(
                        code=code,
                        title=data.get("title", {}).get("@value", "") if isinstance(data.get("title"), dict) else str(data.get("title", "")),
                        module=module,
                        category=data.get("classKind", ""),
                        parent=data.get("parent", [])[0] if data.get("parent") else None,
                        children=[child for child in data.get("child", [])],
                        definition=data.get("definition", {}).get("@value", "") if isinstance(data.get("definition"), dict) else str(data.get("definition", ""))
                    )
                else:
                    logger.warning(f"ICD code lookup failed: {response.status_code} for code {code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error looking up ICD code '{code}': {e}")
            return None

    async def map_namaste_to_icd(self, namaste_code: str, namaste_term: str) -> ICDMappingResponse:
        """Map NAMASTE code to ICD-11 codes"""
        
        try:
            # Use autocode to find ICD mappings
            autocode_result = await self.autocode(namaste_term)
            
            # Determine confidence based on results
            confidence = "low"
            if autocode_result.total > 0:
                # Check for high-confidence matches
                high_confidence_results = [r for r in autocode_result.results if r.score and r.score > 0.8]
                if high_confidence_results:
                    confidence = "high"
                elif autocode_result.total > 1:
                    confidence = "medium"
            
            return ICDMappingResponse(
                namaste_code=namaste_code,
                namaste_term=namaste_term,
                icd_mappings=autocode_result.results,
                mapping_confidence=confidence,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error mapping NAMASTE code '{namaste_code}' to ICD: {e}")
            return ICDMappingResponse(
                namaste_code=namaste_code,
                namaste_term=namaste_term,
                icd_mappings=[],
                mapping_confidence="error",
                timestamp=datetime.now().isoformat()
            )

    async def health_check(self) -> dict:
        """Health check for ICD service"""
        try:
            # Try to get a token
            token = await self.get_access_token()
            if token:
                return {
                    "status": "healthy",
                    "api_base": self.api_base,
                    "token_valid": bool(self.access_token),
                    "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
                }
            else:
                return {"status": "error", "message": "Could not obtain access token"}
        except Exception as e:
            return {"status": "error", "message": str(e)}