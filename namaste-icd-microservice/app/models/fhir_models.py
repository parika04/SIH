from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

# FHIR R4 Models for NAMASTE-ICD Integration

class FHIRCoding(BaseModel):
    system: str
    code: str
    display: str
    version: Optional[str] = None

class FHIRIdentifier(BaseModel):
    use: Optional[str] = None
    type: Optional[Dict] = None
    system: str
    value: str

class FHIRMeta(BaseModel):
    versionId: Optional[str] = None
    lastUpdated: Optional[str] = None
    source: Optional[str] = None
    profile: Optional[List[str]] = []
    security: Optional[List[FHIRCoding]] = []
    tag: Optional[List[FHIRCoding]] = []

class FHIRCodeSystemConcept(BaseModel):
    code: str
    display: str
    definition: Optional[str] = None
    property: Optional[List[Dict]] = []
    concept: Optional[List["FHIRCodeSystemConcept"]] = []

class FHIRCodeSystem(BaseModel):
    resourceType: str = "CodeSystem"
    id: str
    meta: Optional[FHIRMeta] = None
    url: str
    identifier: Optional[List[FHIRIdentifier]] = []
    version: str
    name: str
    title: str
    status: str = "active"
    experimental: bool = False
    date: str
    publisher: str = "Ministry of AYUSH, India"
    contact: Optional[List[Dict]] = []
    description: str
    jurisdiction: Optional[List[Dict]] = []
    purpose: Optional[str] = None
    copyright: Optional[str] = None
    caseSensitive: bool = True
    valueSet: Optional[str] = None
    hierarchyMeaning: str = "is-a"
    compositional: bool = False
    versionNeeded: bool = False
    content: str = "complete"
    supplements: Optional[str] = None
    count: Optional[int] = None
    filter: Optional[List[Dict]] = []
    property: Optional[List[Dict]] = []
    concept: List[FHIRCodeSystemConcept]

class FHIRConceptMapElement(BaseModel):
    code: str
    display: Optional[str] = None
    target: List[Dict]  # Contains code, display, equivalence, etc.

class FHIRConceptMapGroup(BaseModel):
    source: str
    sourceVersion: Optional[str] = None
    target: str
    targetVersion: Optional[str] = None
    element: List[FHIRConceptMapElement]

class FHIRConceptMap(BaseModel):
    resourceType: str = "ConceptMap"
    id: str
    meta: Optional[FHIRMeta] = None
    url: str
    identifier: Optional[List[FHIRIdentifier]] = []
    version: str
    name: str
    title: str
    status: str = "active"
    experimental: bool = False
    date: str
    publisher: str = "Ministry of AYUSH, India"
    contact: Optional[List[Dict]] = []
    description: str
    jurisdiction: Optional[List[Dict]] = []
    purpose: Optional[str] = None
    copyright: Optional[str] = None
    sourceUri: Optional[str] = None
    targetUri: Optional[str] = None
    group: List[FHIRConceptMapGroup]

class FHIRValueSet(BaseModel):
    resourceType: str = "ValueSet"
    id: str
    meta: Optional[FHIRMeta] = None
    url: str
    identifier: Optional[List[FHIRIdentifier]] = []
    version: str
    name: str
    title: str
    status: str = "active"
    experimental: bool = False
    date: str
    publisher: str = "Ministry of AYUSH, India"
    contact: Optional[List[Dict]] = []
    description: str
    jurisdiction: Optional[List[Dict]] = []
    purpose: Optional[str] = None
    copyright: Optional[str] = None
    compose: Dict
    expansion: Optional[Dict] = None

class FHIRCondition(BaseModel):
    resourceType: str = "Condition"
    id: str
    meta: Optional[FHIRMeta] = None
    identifier: Optional[List[FHIRIdentifier]] = []
    clinicalStatus: FHIRCoding
    verificationStatus: Optional[FHIRCoding] = None
    category: Optional[List[FHIRCoding]] = []
    severity: Optional[FHIRCoding] = None
    code: FHIRCoding  # NAMASTE code
    bodySite: Optional[List[FHIRCoding]] = []
    subject: Dict  # Patient reference
    encounter: Optional[Dict] = None  # Encounter reference
    onsetDateTime: Optional[str] = None
    recordedDate: Optional[str] = None
    recorder: Optional[Dict] = None  # Practitioner reference
    evidence: Optional[List[Dict]] = []
    note: Optional[List[Dict]] = []

class FHIRBundle(BaseModel):
    resourceType: str = "Bundle"
    id: str
    meta: Optional[FHIRMeta] = None
    identifier: Optional[FHIRIdentifier] = None
    type: str  # collection, searchset, history, etc.
    timestamp: Optional[str] = None
    total: Optional[int] = None
    link: Optional[List[Dict]] = []
    entry: List[Dict]  # Bundle entries

class FHIROperationOutcome(BaseModel):
    resourceType: str = "OperationOutcome"
    id: Optional[str] = None
    meta: Optional[FHIRMeta] = None
    issue: List[Dict]

# Update forward references
FHIRCodeSystemConcept.model_rebuild()