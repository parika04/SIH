import pandas as pd
import os

def load_namaste_csvs(filepaths: dict):
    """
    filepaths = {
        "ayurveda": "data/ayurveda.csv",
        "siddha": "data/siddha.csv",
        "unani": "data/unani.csv"
    }
    """
    dfs = []
    for system, path in filepaths.items():
        if not os.path.exists(path):
            print(f"⚠️ Missing file: {path}")
            continue

        df = pd.read_csv(path)

        if system == "unani":
            df = df.rename(columns={
                "NUMC_ID": "id",
                "NUMC_CODE": "code",
                "NUMC_TERM": "term"
            })
        elif system == "siddha":
            df = df.rename(columns={
                "NAMC_ID": "id",
                "NAMC_CODE": "code",
                "NAMC_TERM": "term"
            })
        elif system == "ayurveda":
            df = df.rename(columns={
                "NAMC_ID": "id",
                "NAMC_CODE": "code",
                "NAMC_term": "term"
            })
        else:
            continue

        df["system"] = system
        dfs.append(df[["id", "code", "term", "system"]])

    return pd.concat(dfs, ignore_index=True)

def get_code_details(df, code: str):
    row = df[df["code"] == code]
    if row.empty:
        return None
    return row.iloc[0].to_dict()
