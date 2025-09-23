import json
import time
from .icd_client import get_token, icd_autocode

def build_conceptmap(df, output_file="output/conceptmap_namaste_icd11.json"):
    token = get_token()

    conceptmap = {
        "resourceType": "ConceptMap",
        "id": "namaste-to-icd11",
        "status": "active",
        "sourceUri": "http://example.org/fhir/CodeSystem/namaste",
        "targetUri": "http://id.who.int/icd/release/11/mms",
        "group": [
            {
                "source": "http://example.org/fhir/CodeSystem/namaste",
                "target": "http://id.who.int/icd/release/11/mms",
                "element": []
            }
        ]
    }

    elements = conceptmap["group"][0]["element"]

    for _, row in df.iterrows():
        namc_code = row.get("NAMC_CODE")
        namc_term = row.get("NAMC_TERM")

        if not namc_term:
            continue

        result = icd_autocode(namc_term, token)
        time.sleep(0.3)  # avoid API throttling

        if result and "destinationEntities" in result:
            targets = []
            for ent in result["destinationEntities"]:
                targets.append({
                    "code": ent.get("code"),
                    "display": ent.get("label"),
                    "equivalence": "relatedto"
                })

            elements.append({
                "code": namc_code,
                "display": namc_term,
                "target": targets
            })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(conceptmap, f, indent=2, ensure_ascii=False)

    print(f"✅ ConceptMap saved to {output_file}")
