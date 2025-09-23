from fastapi import FastAPI
from app.namaste_loader import load_namaste_csvs, get_code_details
from app.icd_client import get_token, icd_autocode
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from app.routers import ayush, icd, fhir

app = FastAPI(title="AYUSH–ICD Terminology API")

# Register routers
app.include_router(ayush.router)
app.include_router(icd.router)
app.include_router(fhir.router)

@app.get("/lookup/{code}")
async def lookup_code(code: str):
    result = df[df["code"] == code]
    if not result.empty:
        data = result.iloc[0].to_dict()
        return JSONResponse(content=data, media_type="application/json; charset=utf-8")
    return JSONResponse(content={"error": "Code not found"}, status_code=404)

app = FastAPI(title="NAMASTE ↔ ICD-11 Microservice")

# Load NAMASTE CSVs
df = load_namaste_csvs({
    "ayurveda": "data/ayurveda.csv",
    "siddha": "data/siddha.csv",
    "unani": "data/unani.csv"
})


@app.get("/")
def root():
    return {"msg": "NAMASTE ↔ ICD-11 Terminology Microservice"}

@app.get("/lookup/{namc_code}")
def lookup_code(namc_code: str):
    row = get_code_details(df, namc_code)
    if not row:
        return {"error": "Code not found"}
    return row

@app.get("/map/{namc_code}")
def map_to_icd(namc_code: str):
    row = get_code_details(df, namc_code)
    if not row:
        return {"error": "Code not found"}

    term = row["NAMC_TERM"]
    token = get_token()
    icd_result = icd_autocode(term, token)

    if not icd_result or "destinationEntities" not in icd_result:
        return {"namc_code": namc_code, "namc_term": term, "icd_mapping": None}

    mapped = [
        {"icd_code": e.get("code"), "label": e.get("label")}
        for e in icd_result["destinationEntities"]
    ]

    return {
        "namc_code": namc_code,
        "namc_term": term,
        "icd_mapping": mapped
    }
