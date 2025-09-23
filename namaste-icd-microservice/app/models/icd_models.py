from typing import List, Optional
from pydantic import BaseModel


class ICDCode(BaseModel):
    code: str
    title: str
    module: str  # "tm2" or "biomedicine"
    category: Optional[str] = None
    parent: Optional[str] = None
    children: Optional[List[str]] = []
    definition: Optional[str] = None


class ICDAutocodeResult(BaseModel):
    icd_code: str
    title: str
    module: str  # "tm2" or "biomedicine"
    score: Optional[float] = None


class ICDAutocodeResponse(BaseModel):
    term: str
    results: List[ICDAutocodeResult] = []
    total: int = 0


class ICDMappingResponse(BaseModel):
    namaste_code: str
    namaste_term: str
    icd_mappings: List[ICDAutocodeResult] = []
    mapping_confidence: str
    timestamp: str


