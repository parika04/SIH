# NAMASTE ↔ ICD-11 Microservice

This project is a lightweight **terminology microservice** that ingests
**AYUSH NAMASTE codes (Ayurveda, Siddha, Unani)** and maps them to
**ICD-11 TM2 + Biomedicine codes** via the official WHO ICD API.

## Features
- Load NAMASTE CSVs → FHIR CodeSystem
- Auto-map to ICD-11 using WHO ICD API `autocode` endpoint
- Expose FastAPI endpoints:
  - `/lookup/{namc_code}` → see NAMASTE details
  - `/map/{namc_code}` → map to ICD-11 automatically
- Build and save a FHIR `ConceptMap` JSON

## Setup
```bash
git clone <repo>
cd namaste-icd-microservice

# Install dependencies
pip install -r requirements.txt

# Run FastAPI
uvicorn app.main:app --reload
