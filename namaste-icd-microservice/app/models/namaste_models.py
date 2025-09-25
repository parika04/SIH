from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class NAMASTECode:
    code: str
    term: str
    system: str  # ayurveda | siddha | unani
    short_definition: Optional[str] = None
    long_definition: Optional[str] = None
    ontology_branches: Optional[str] = None
    tamil_term: Optional[str] = None
    arabic_term: Optional[str] = None
    devanagari_term: Optional[str] = None
    diacritical_term: Optional[str] = None
    reference: Optional[str] = None


@dataclass
class NAMASTELookupResponse:
    code: str
    term: str
    system: str
    definitions: Dict[str, str]
    additional_terms: Dict[str, str]
    found: bool


@dataclass
class NAMASTESearchResult:
    code: str
    term: str
    system: str
    score: float


@dataclass
class NAMASTESearchResponse:
    results: List[NAMASTESearchResult]
    total: int
    query: str


