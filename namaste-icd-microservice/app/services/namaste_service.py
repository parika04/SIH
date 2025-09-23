import pandas as pd
import logging
from datetime import datetime
import os
from typing import Optional, List, Dict

from app.config import settings

logger = logging.getLogger(__name__)

class NAMASTEService:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.loaded_at: Optional[datetime] = None

    async def load_data(self):
        """
        Load and normalize AYUSH CSVs into a single DataFrame.
        """
        files = {
            "ayurveda": settings.ayurveda_csv,
            "siddha": settings.siddha_csv,
            "unani": settings.unani_csv
        }
        frames = []
        for system, path in files.items():
            if not os.path.exists(path):
                logger.warning(f"{path} not found")
                continue
            df = pd.read_csv(path)
            df["system"] = system
            # Normalize code & term columns
            df = self._normalize(df, system)
            frames.append(df)
        if not frames:
            raise RuntimeError("No NAMASTE CSV files loaded")
        self.df = pd.concat(frames, ignore_index=True)
        self.loaded_at = datetime.utcnow()
        logger.info(f"Loaded {len(self.df)} NAMASTE terms")

    def _normalize(self, df: pd.DataFrame, system: str) -> pd.DataFrame:
        # Map column names to 'code' and 'term'
        col_map = {}
        if system == "ayurveda":
            col_map = {"NAMC_CODE": "code", "NAMC_term": "term"}
        elif system == "siddha":
            col_map = {"NAMC_CODE": "code", "NAMC_TERM": "term"}
        elif system == "unani":
            col_map = {"NUMC_CODE": "code", "NUMC_TERM": "term"}
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        return df

    async def lookup_code(self, code: str) -> Optional[Dict]:
        """
        Lookup a single NAMASTE code.
        """
        if self.df is None:
            await self.load_data()
        subset = self.df[self.df["code"] == code]
        if subset.empty:
            return None
        row = subset.iloc[0]
        return {
            "code": row["code"],
            "term": row["term"],
            "system": row["system"]
        }

    async def search_terms(self, query: str, system: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Search NAMASTE terms by substring match.
        """
        if self.df is None:
            await self.load_data()
        df = self.df
        if system:
            df = df[df["system"] == system]
        mask = df["term"].str.contains(query, case=False, na=False)
        results = df[mask].head(limit)
        return results.to_dict(orient="records")

    async def health_check(self) -> Dict:
        if self.df is None:
            return {"status": "error", "message": "Data not loaded"}
        return {
            "status": "healthy",
            "count": len(self.df),
            "loaded_at": self.loaded_at.isoformat()
        }

    async def get_all_codes(self, system: Optional[str] = None) -> List[Dict]:
        """
        Return all codes, optionally filtered by system.
        """
        if self.df is None:
            await self.load_data()
        df = self.df
        if system:
            df = df[df["system"] == system]
        return df[["code", "term", "system"]].to_dict(orient="records")