from fastapi import APIRouter

router = APIRouter(prefix="/icd", tags=["ICD"])

@router.get("/search")
async def search_icd(term: str):
    return {"term": term, "message": "ICD search working!"}
