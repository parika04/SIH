from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ICDCode:
    code: str
    title: str
    module: str  # "tm2" or "biomedicine"
    category: Optional[str] = None
    parent: Optional[str] = None
    children: Optional[List[str]] = None
    definition: Optional[str] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


@dataclass
class ICDAutocodeResult:
    icd_code: str
    title: str
    module: str  # "tm2" or "biomedicine"
    score: Optional[float] = None


@dataclass
class ICDAutocodeResponse:
    term: str
    results: List[ICDAutocodeResult]
    total: int

    def __post_init__(self):
        if self.results is None:
            self.results = []


@dataclass
class ICDMappingResponse:
    namaste_code: str
    namaste_term: str
    icd_mappings: List[ICDAutocodeResult]
    mapping_confidence: str
    timestamp: str

    def __post_init__(self):
        if self.icd_mappings is None:
            self.icd_mappings = []