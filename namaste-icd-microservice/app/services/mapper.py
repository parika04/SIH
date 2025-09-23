import httpx

ICD_API_BASE = "https://id.who.int/icd/release/11"

# Fake ConceptMap dictionary (for now, expand later)
AYUSH_TO_ICD = {
    "A-1": {"code": "8A80", "display": "Tension-type headache"},
    "AAA1.1": {"code": "XA12", "display": "Hepatomegaly"}
}


async def translate_ayush_to_icd(code: str):
    """
    Map AYUSH code to ICD-11.
    First check static ConceptMap, fallback to WHO ICD API.
    """
    # 1. Static ConceptMap lookup
    if code in AYUSH_TO_ICD:
        return AYUSH_TO_ICD[code]

    # 2. Fallback: WHO ICD API autocode (text search)
    async with httpx.AsyncClient() as client:
        url = f"{ICD_API_BASE}/autocode"
        resp = await client.get(url, params={"q": code})
        if resp.status_code == 200:
            data = resp.json()
            if data.get("destinationEntities"):
                match = data["destinationEntities"][0]
                return {
                    "code": match["id"].split("/")[-1],
                    "display": match["title"]["@value"]
                }
    return None
