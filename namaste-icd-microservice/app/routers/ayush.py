import os
import pandas as pd
from fastapi import APIRouter, HTTPException
import pandas as pd

print("🚀 DEBUG: Loading AYUSH CSVs...")

# Adjust these paths to your actual CSVs
unani_path = "data/unani.csv"
siddha_path = "data/siddha.csv"
ayurveda_path = "data/ayurveda.csv"

try:
    unani_df = pd.read_csv(unani_path)
    print("🔎 Unani columns:", unani_df.columns.tolist())
except Exception as e:
    print("❌ Error loading Unani:", e)

try:
    siddha_df = pd.read_csv(siddha_path)
    print("🔎 Siddha columns:", siddha_df.columns.tolist())
except Exception as e:
    print("❌ Error loading Siddha:", e)

try:
    ayurveda_df = pd.read_csv(ayurveda_path)
    print("🔎 Ayurveda columns:", ayurveda_df.columns.tolist())
except Exception as e:
    print("❌ Error loading Ayurveda:", e)

router = APIRouter()

base_dir = os.path.dirname(os.path.abspath(__file__))

def load_csvs():
    dfs = []

    try:
        # Unani
        unani = pd.read_csv(os.path.join(base_dir, "../../data/unani.csv"))
        unani = unani.rename(columns={
            "NUMC_CODE": "CODE",
            "NUMC_TERM": "TERM"
        })
        dfs.append(unani[["CODE", "TERM"]])

        # Siddha
        siddha = pd.read_csv(os.path.join(base_dir, "../../data/siddha.csv"))
        siddha = siddha.rename(columns={
            "NAMC_CODE": "CODE",
            "NAMC_TERM": "TERM"
        })
        dfs.append(siddha[["CODE", "TERM"]])

        # Ayurveda
        ayurveda = pd.read_csv(os.path.join(base_dir, "../../data/ayurveda.csv"))
        ayurveda = ayurveda.rename(columns={
            "NAMC_CODE": "CODE",
            "NAMC_term": "TERM"  # lowercase t in your Ayurveda file
        })
        dfs.append(ayurveda[["CODE", "TERM"]])

    except Exception as e:
        print(f"❌ CSV loading error: {e}")

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame(columns=["CODE", "TERM"])

ayush_df = load_csvs()

@router.get("/lookup/{code}")
async def lookup_code(code: str):
    row = ayush_df[ayush_df["CODE"] == code]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Code {code} not found")
    return row.to_dict(orient="records")[0]

@router.get("/map/{namc_code}")
async def map_to_icd(namc_code: str):
    row = ayush_df[ayush_df["CODE"] == namc_code]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"NAMASTE code {namc_code} not found")

    term = row.iloc[0]["TERM"]

    # For now, placeholder ICD mapping
    return {
        "namc_code": namc_code,
        "namc_term": term,
        "icd_mapping": {
            "icd_code": "Dummy-123",
            "icd_term": f"ICD placeholder for {term}"
        }
    }
