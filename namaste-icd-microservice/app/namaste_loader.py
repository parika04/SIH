import pandas as pd

def load_namaste_csvs(paths: dict) -> pd.DataFrame:
    frames = []
    for key, path in paths.items():
        df = pd.read_csv(path)
        # Standardize code column
        if "NAMC_CODE" in df.columns:
            df = df.rename(columns={"NAMC_CODE": "code"})
        elif "NUMC_CODE" in df.columns:
            df = df.rename(columns={"NUMC_CODE": "code"})
        else:
            # fallback
            df = df.rename(columns={df.columns[2]: "code"})
        # Standardize term column
        if "NAMC_TERM" in df.columns:
            df = df.rename(columns={"NAMC_TERM": "term"})
        elif "NUMC_TERM" in df.columns:
            df = df.rename(columns={"NUMC_TERM": "term"})
        elif "NAMC_term" in df.columns:
            df = df.rename(columns={"NAMC_term": "term"})
        else:
            # fallback to fourth column
            df = df.rename(columns={df.columns[3]: "term"})
        # Keep only code, term, plus any other useful metadata
        df = df[["code", "term"] + [c for c in df.columns if c not in ["code", "term"]]]
        frames.append(df)

    # Concatenate all AYUSH systems
    combined = pd.concat(frames, ignore_index=True)
    return combined

def get_code_details(df: pd.DataFrame, code: str) -> dict | None:
    result = df[df["code"] == code]
    if result.empty:
        return None
    return result.iloc[0].to_dict()
