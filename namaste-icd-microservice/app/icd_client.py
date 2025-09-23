import requests
from .config import TOKEN_ENDPOINT, CLIENT_ID, CLIENT_SECRET, SCOPE, RELEASE, LINEARIZATION

def get_token():
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE,
        "grant_type": "client_credentials"
    }
    r = requests.post(TOKEN_ENDPOINT, data=payload, verify=False)
    r.raise_for_status()
    return r.json()["access_token"]

def icd_autocode(term: str, token: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2"
    }
    uri = f"https://id.who.int/icd/release/11/{RELEASE}/{LINEARIZATION}/autocode"
    params = {"q": term}
    r = requests.get(uri, headers=headers, params=params, verify=False)
    if r.status_code == 200:
        return r.json()
    return None
