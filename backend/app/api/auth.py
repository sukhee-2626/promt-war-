import json, hmac, hashlib, base64, time
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

SECRET = "supersecret" # ponytail: Replace with os.environ["JWT_SECRET"]; use python-jose if features grow.

def create_jwt(payload: Dict) -> str:
    payload.setdefault("exp", time.time() + 3600)
    def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")
    h, c = b64({"alg": "HS256", "typ": "JWT"}), b64(payload)
    sig = base64.urlsafe_b64encode(hmac.new(SECRET.encode(), f"{h}.{c}".encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{h}.{c}.{sig}"

def decode_jwt(token: str) -> Dict:
    try:
        h, c, s = token.split(".")
        if base64.urlsafe_b64encode(hmac.new(SECRET.encode(), f"{h}.{c}".encode(), hashlib.sha256).digest()).decode().rstrip("=") != s: raise Exception
        payload = json.loads(base64.urlsafe_b64decode(c + "=="))
        if time.time() > payload.get("exp", 0): raise Exception
        return payload
    except: raise HTTPException(status_code=401, detail="Invalid token")

security = HTTPBearer()
def get_current_user(creds: HTTPAuthorizationCredentials = Security(security)):
    return decode_jwt(creds.credentials)
