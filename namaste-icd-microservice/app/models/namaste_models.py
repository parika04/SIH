from typing import List, Optional
from pydantic import BaseModel


class NAMASTECode(BaseModel):
    code: str
    term: str
    system: str  # ayurveda | siddha | unani


class NAMASTELookupResponse(BaseModel):
    code: str
    term: str
    system: str


class NAMASTESearchResponse(BaseModel):
    results: List[NAMASTECode]
    total: int


