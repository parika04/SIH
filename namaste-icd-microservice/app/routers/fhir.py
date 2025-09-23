from fastapi import APIRouter, Query
from app.services.mapper import translate_ayush_to_icd

router = APIRouter(prefix="/fhir", tags=["FHIR"])


@router.get("/ConceptMap/$translate")
async def translate(
    code: str = Query(..., description="AYUSH code"),
    system: str = Query("ayush", description="Source system (default: ayush)")
):
    """
    FHIR $translate operation: AYUSH -> ICD
    """
    if system != "ayush":
        return {"result": False, "message": "Unsupported system"}

    icd_match = await translate_ayush_to_icd(code)

    if not icd_match:
        return {"result": False, "message": "No mapping found"}

    return {
        "resourceType": "Parameters",
        "parameter": [
            {"name": "result", "valueBoolean": True},
            {
                "name": "match",
                "part": [
                    {"name": "equivalence", "valueCode": "related-to"},
                    {
                        "name": "concept",
                        "valueCoding": {
                            "system": "http://id.who.int/icd/release/11/mms",
                            "code": icd_match["code"],
                            "display": icd_match["display"]
                        }
                    }
                ]
            }
        ]
    }
