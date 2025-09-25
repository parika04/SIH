from typing import Dict, List, Optional, Any
from datetime import datetime

# FHIR R4 Helper Functions for NAMASTE-ICD Integration

def create_fhir_coding(system: str, code: str, display: str, version: Optional[str] = None) -> Dict[str, Any]:
    """Create a FHIR Coding object"""
    coding = {
        "system": system,
        "code": code,
        "display": display
    }
    if version:
        coding["version"] = version
    return coding

def create_fhir_identifier(use: Optional[str], system: str, value: str, type_dict: Optional[Dict] = None) -> Dict[str, Any]:
    """Create a FHIR Identifier object"""
    identifier = {
        "system": system,
        "value": value
    }
    if use:
        identifier["use"] = use
    if type_dict:
        identifier["type"] = type_dict
    return identifier

def create_fhir_meta(version_id: Optional[str] = None, last_updated: Optional[str] = None, 
                    source: Optional[str] = None, profile: Optional[List[str]] = None,
                    security: Optional[List[Dict]] = None, tag: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Create a FHIR Meta object"""
    meta = {}
    if version_id:
        meta["versionId"] = version_id
    if last_updated:
        meta["lastUpdated"] = last_updated
    if source:
        meta["source"] = source
    if profile:
        meta["profile"] = profile
    if security:
        meta["security"] = security
    if tag:
        meta["tag"] = tag
    return meta

def create_fhir_codesystem(id: str, url: str, version: str, name: str, title: str, 
                          description: str, date: str, concept: List[Dict],
                          meta: Optional[Dict] = None, identifier: Optional[List[Dict]] = None,
                          publisher: str = "Ministry of AYUSH, India") -> Dict[str, Any]:
    """Create a FHIR CodeSystem object"""
    codesystem = {
        "resourceType": "CodeSystem",
        "id": id,
        "url": url,
        "version": version,
        "name": name,
        "title": title,
        "status": "active",
        "experimental": False,
        "date": date,
        "publisher": publisher,
        "description": description,
        "caseSensitive": True,
        "hierarchyMeaning": "is-a",
        "compositional": False,
        "versionNeeded": False,
        "content": "complete",
        "concept": concept
    }
    if meta:
        codesystem["meta"] = meta
    if identifier:
        codesystem["identifier"] = identifier
    return codesystem

def create_fhir_conceptmap(id: str, url: str, version: str, name: str, title: str,
                          description: str, date: str, group: List[Dict],
                          meta: Optional[Dict] = None, identifier: Optional[List[Dict]] = None,
                          publisher: str = "Ministry of AYUSH, India") -> Dict[str, Any]:
    """Create a FHIR ConceptMap object"""
    conceptmap = {
        "resourceType": "ConceptMap",
        "id": id,
        "url": url,
        "version": version,
        "name": name,
        "title": title,
        "status": "active",
        "experimental": False,
        "date": date,
        "publisher": publisher,
        "description": description,
        "group": group
    }
    if meta:
        conceptmap["meta"] = meta
    if identifier:
        conceptmap["identifier"] = identifier
    return conceptmap

def create_fhir_valueset(id: str, url: str, version: str, name: str, title: str,
                        description: str, date: str, compose: Dict,
                        meta: Optional[Dict] = None, identifier: Optional[List[Dict]] = None,
                        publisher: str = "Ministry of AYUSH, India") -> Dict[str, Any]:
    """Create a FHIR ValueSet object"""
    valueset = {
        "resourceType": "ValueSet",
        "id": id,
        "url": url,
        "version": version,
        "name": name,
        "title": title,
        "status": "active",
        "experimental": False,
        "date": date,
        "publisher": publisher,
        "description": description,
        "compose": compose
    }
    if meta:
        valueset["meta"] = meta
    if identifier:
        valueset["identifier"] = identifier
    return valueset

def create_fhir_condition(id: str, clinical_status: Dict, code: Dict, subject: Dict,
                         verification_status: Optional[Dict] = None, category: Optional[List[Dict]] = None,
                         severity: Optional[Dict] = None, body_site: Optional[List[Dict]] = None,
                         encounter: Optional[Dict] = None, onset_date_time: Optional[str] = None,
                         recorded_date: Optional[str] = None, recorder: Optional[Dict] = None,
                         evidence: Optional[List[Dict]] = None, note: Optional[List[Dict]] = None,
                         meta: Optional[Dict] = None, identifier: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Create a FHIR Condition object"""
    condition = {
        "resourceType": "Condition",
        "id": id,
        "clinicalStatus": clinical_status,
        "code": code,
        "subject": subject
    }
    if meta:
        condition["meta"] = meta
    if identifier:
        condition["identifier"] = identifier
    if verification_status:
        condition["verificationStatus"] = verification_status
    if category:
        condition["category"] = category
    if severity:
        condition["severity"] = severity
    if body_site:
        condition["bodySite"] = body_site
    if encounter:
        condition["encounter"] = encounter
    if onset_date_time:
        condition["onsetDateTime"] = onset_date_time
    if recorded_date:
        condition["recordedDate"] = recorded_date
    if recorder:
        condition["recorder"] = recorder
    if evidence:
        condition["evidence"] = evidence
    if note:
        condition["note"] = note
    return condition

def create_fhir_bundle(id: str, type: str, entry: List[Dict], identifier: Optional[Dict] = None,
                      timestamp: Optional[str] = None, total: Optional[int] = None,
                      link: Optional[List[Dict]] = None, meta: Optional[Dict] = None) -> Dict[str, Any]:
    """Create a FHIR Bundle object"""
    bundle = {
        "resourceType": "Bundle",
        "id": id,
        "type": type,
        "entry": entry
    }
    if meta:
        bundle["meta"] = meta
    if identifier:
        bundle["identifier"] = identifier
    if timestamp:
        bundle["timestamp"] = timestamp
    if total:
        bundle["total"] = total
    if link:
        bundle["link"] = link
    return bundle

def create_fhir_operation_outcome(issue: List[Dict], id: Optional[str] = None, meta: Optional[Dict] = None) -> Dict[str, Any]:
    """Create a FHIR OperationOutcome object"""
    outcome = {
        "resourceType": "OperationOutcome",
        "issue": issue
    }
    if id:
        outcome["id"] = id
    if meta:
        outcome["meta"] = meta
    return outcome