# NAMASTE Service - Core terminology management
import pandas as pd
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

from app.config import settings
from app.models.namaste_models import (
    NAMASTECode, NAMASTELookupResponse, NAMASTESearchResponse, 
    NAMASTESearchResult
)

logger = logging.getLogger(__name__)

class NAMASTEService:
    def __init__(self):
        self.namaste_data: Optional[pd.DataFrame] = None
        self.loaded_at: Optional[datetime] = None

    async def load_data(self):
        """Load NAMASTE CSV data from all three systems"""
        try:
            logger.info("Loading NAMASTE data...")
            
            # Load individual CSV files
            dataframes = []
            
            # Ayurveda
            if os.path.exists(settings.ayurveda_csv):
                ayurveda_df = pd.read_csv(settings.ayurveda_csv)
                ayurveda_df = self._normalize_ayurveda_columns(ayurveda_df)
                ayurveda_df['system'] = 'ayurveda'
                dataframes.append(ayurveda_df)
                logger.info(f"Loaded {len(ayurveda_df)} Ayurveda terms")
            
            # Siddha
            if os.path.exists(settings.siddha_csv):
                siddha_df = pd.read_csv(settings.siddha_csv)
                siddha_df = self._normalize_siddha_columns(siddha_df)
                siddha_df['system'] = 'siddha'
                dataframes.append(siddha_df)
                logger.info(f"Loaded {len(siddha_df)} Siddha terms")
            
            # Unani
            if os.path.exists(settings.unani_csv):
                unani_df = pd.read_csv(settings.unani_csv)
                unani_df = self._normalize_unani_columns(unani_df)
                unani_df['system'] = 'unani'
                dataframes.append(unani_df)
                logger.info(f"Loaded {len(unani_df)} Unani terms")
            
            if not dataframes:
                raise Exception("No NAMASTE CSV files found")
            
            # Combine all dataframes
            self.namaste_data = pd.concat(dataframes, ignore_index=True)
            self.loaded_at = datetime.now()
            
            logger.info(f"Successfully loaded {len(self.namaste_data)} total NAMASTE terms")
            
        except Exception as e:
            logger.error(f"Error loading NAMASTE data: {e}")
            raise

    def _normalize_ayurveda_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Ayurveda CSV columns to standard format"""
        column_mapping = {
            'NAMC_CODE': 'code',
            'NAMC_term': 'term',  # Note: lowercase 't' in ayurveda
            'Short_definition': 'short_definition',
            'Long_definition': 'long_definition',
            'NAMC_term_diacritical': 'diacritical_term',
            'NAMC_term_DEVANAGARI': 'devanagari_term',
            'Ontology_branches': 'ontology_branches'
        }
        
        # Rename columns that exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df

    def _normalize_siddha_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Siddha CSV columns to standard format"""
        column_mapping = {
            'NAMC_CODE': 'code',
            'NAMC_TERM': 'term',
            'Tamil_term': 'tamil_term',
            'Short_definition': 'short_definition',
            'Long_definition': 'long_definition',
            'Reference': 'reference'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df

    def _normalize_unani_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Unani CSV columns to standard format"""
        column_mapping = {
            'NUMC_CODE': 'code',
            'NUMC_TERM': 'term',
            'Arabic_term': 'arabic_term',
            'Short_definition': 'short_definition',
            'Long_definition': 'long_definition'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df

    async def lookup_code(self, code: str) -> Optional[NAMASTELookupResponse]:
        """Lookup NAMASTE code details"""
        if self.namaste_data is None:
            await self.load_data()
        
        try:
            # Find the code in the dataframe
            result = self.namaste_data[self.namaste_data['code'] == code]
            
            if result.empty:
                return NAMASTELookupResponse(
                    code=code,
                    term="",
                    system="",
                    definitions={},
                    additional_terms={},
                    found=False
                )
            
            row = result.iloc[0]
            
            # Build definitions dictionary
            definitions = {}
            if pd.notna(row.get('short_definition')):
                definitions['short'] = str(row['short_definition'])
            if pd.notna(row.get('long_definition')):
                definitions['long'] = str(row['long_definition'])
            
            # Build additional terms dictionary
            additional_terms = {}
            for term_type in ['tamil_term', 'arabic_term', 'devanagari_term', 'diacritical_term']:
                if pd.notna(row.get(term_type)):
                    additional_terms[term_type] = str(row[term_type])
            
            return NAMASTELookupResponse(
                code=code,
                term=str(row['term']),
                system=str(row['system']),
                definitions=definitions,
                additional_terms=additional_terms,
                found=True
            )
            
        except Exception as e:
            logger.error(f"Error looking up code {code}: {e}")
            return None

    async def search_terms(self, query: str, system: Optional[str] = None, limit: int = 10) -> NAMASTESearchResponse:
        """Search NAMASTE terms"""
        if self.namaste_data is None:
            await self.load_data()
        
        try:
            df = self.namaste_data
            
            # Filter by system if specified
            if system:
                df = df[df['system'] == system]
            
            # Search in term column (case insensitive)
            mask = df['term'].str.contains(query, case=False, na=False)
            
            # Also search in definitions if available
            if 'short_definition' in df.columns:
                mask |= df['short_definition'].str.contains(query, case=False, na=False)
            if 'long_definition' in df.columns:
                mask |= df['long_definition'].str.contains(query, case=False, na=False)
            
            results_df = df[mask].head(limit)
            
            # Convert to search results
            results = []
            for _, row in results_df.iterrows():
                # Simple scoring based on exact matches
                score = 0.5
                if query.lower() in str(row['term']).lower():
                    score += 0.3
                if query.lower() == str(row['term']).lower():
                    score += 0.2
                
                results.append(NAMASTESearchResult(
                    code=str(row['code']),
                    term=str(row['term']),
                    system=str(row['system']),
                    score=min(score, 1.0)
                ))
            
            # Sort by score
            results.sort(key=lambda x: x.score, reverse=True)
            
            return NAMASTESearchResponse(
                results=results,
                total=len(results),
                query=query
            )
            
        except Exception as e:
            logger.error(f"Error searching terms with query '{query}': {e}")
            return NAMASTESearchResponse(results=[], total=0, query=query)

    async def get_all_codes(self, system: Optional[str] = None) -> List[NAMASTECode]:
        """Get all NAMASTE codes, optionally filtered by system"""
        if self.namaste_data is None:
            await self.load_data()
        
        try:
            df = self.namaste_data
            if system:
                df = df[df['system'] == system]
            
            codes = []
            for _, row in df.iterrows():
                code = NAMASTECode(
                    code=str(row['code']),
                    term=str(row['term']),
                    system=str(row['system']),
                    short_definition=str(row.get('short_definition', '')) if pd.notna(row.get('short_definition')) else None,
                    long_definition=str(row.get('long_definition', '')) if pd.notna(row.get('long_definition')) else None,
                    ontology_branches=str(row.get('ontology_branches', '')) if pd.notna(row.get('ontology_branches')) else None,
                    tamil_term=str(row.get('tamil_term', '')) if pd.notna(row.get('tamil_term')) else None,
                    arabic_term=str(row.get('arabic_term', '')) if pd.notna(row.get('arabic_term')) else None,
                    devanagari_term=str(row.get('devanagari_term', '')) if pd.notna(row.get('devanagari_term')) else None,
                    diacritical_term=str(row.get('diacritical_term', '')) if pd.notna(row.get('diacritical_term')) else None,
                    reference=str(row.get('reference', '')) if pd.notna(row.get('reference')) else None
                )
                codes.append(code)
            
            return codes
            
        except Exception as e:
            logger.error(f"Error getting all codes: {e}")
            return []

    async def health_check(self) -> dict:
        """Health check for NAMASTE service"""
        try:
            if self.namaste_data is None:
                return {"status": "error", "message": "Data not loaded"}
            
            return {
                "status": "healthy",
                "records_count": len(self.namaste_data),
                "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
                "systems": self.namaste_data['system'].unique().tolist()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}