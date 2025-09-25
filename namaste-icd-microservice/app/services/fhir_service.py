import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

from app.config import settings
from app.models.fhir_models import (
    create_fhir_codesystem, create_fhir_conceptmap, create_fhir_coding, 
    create_fhir_identifier, create_fhir_meta, create_fhir_valueset
)

logger = logging.getLogger(__name__)

class FHIRService:
    def __init__(self):
        self.output_dir = settings.fhir_resources_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def initialize_resources(self):
        """
        Pre-generate CodeSystem and ConceptMap JSON and save to disk.
        """
        await self._generate_codesystem()
        await self._generate_conceptmap()

    async def _generate_codesystem(self):
        """
        Build and save the NAMASTE CodeSystem resource.
        """
        cs = create_fhir_codesystem(
            id="namaste-codesystem",
            url=f"{settings.fhir_base_url}/CodeSystem/namaste",
            version="1.0.0",
            name="NAMASTECodeSystem",
            title="NAMASTE AYUSH Terminology",
            description="AYUSH NAMASTE code system (Ayurveda, Siddha, Unani)",
            date=datetime.utcnow().isoformat(),
            concept=[]  # fill with actual concepts elsewhere
        )
        path = os.path.join(self.output_dir, "CodeSystem-namaste.json")
        with open(path, "w", encoding="utf-8") as f:
            import json
            f.write(json.dumps(cs, indent=2))

    async def _generate_conceptmap(self):
        """
        Build and save the NAMASTE-ICD ConceptMap.
        """
        cm = create_fhir_conceptmap(
            id="namaste-icd-mapping",
            url=f"{settings.fhir_base_url}/ConceptMap/namaste-icd",
            version="1.0.0",
            name="NAMASTEtoICD",
            title="NAMASTE to ICD-11 Mapping",
            description="Mapping between AYUSH NAMASTE codes and ICD-11 codes",
            date=datetime.utcnow().isoformat(),
            group=[]  # populate mapping groups elsewhere
        )
        path = os.path.join(self.output_dir, "ConceptMap-namaste-icd.json")
        with open(path, "w", encoding="utf-8") as f:
            import json
            f.write(json.dumps(cm, indent=2))

    async def get_capability_statement(self) -> Dict[str, Any]:
        """
        Return a basic FHIR CapabilityStatement.
        """
        return {
            "resourceType": "CapabilityStatement",
            "status": "active",
            "date": datetime.utcnow().isoformat(),
            "fhirVersion": settings.fhir_version,
            "format": ["json"]
        }

    async def health_check(self) -> Dict:
        """
        Health check for FHIR resource availability.
        """
        files = os.listdir(self.output_dir)
        return {
            "status": "healthy" if files else "error",
            "resources_generated": files
        }
