# OAuth2 Authentication with ABHA Integration
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

class OAuth2Handler:
    def __init__(self):
        self.abha_base_url = settings.abha_base_url
        self.jwt_secret_key = settings.jwt_secret_key
        self.jwt_algorithm = settings.jwt_algorithm
        self.token_expire_minutes = settings.access_token_expire_minutes

    async def verify_abha_token(self, token: str) -> dict:
        """Verify ABHA token with ABDM APIs"""
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.abha_base_url}/api/v1/auth/verify",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"ABHA token verification failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error verifying ABHA token: {e}")
            return None

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.jwt_algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return payload
        except jwt.PyJWTError:
            return None

oauth2_handler = OAuth2Handler()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        
        # First try to verify as local JWT token
        payload = oauth2_handler.verify_token(token)
        if payload:
            # Log audit trail
            logger.info(f"JWT authentication successful for user: {payload.get('sub')}")
            return payload
        
        # If JWT verification fails, try ABHA token verification
        abha_user = await oauth2_handler.verify_abha_token(token)
        if abha_user:
            logger.info(f"ABHA authentication successful for user: {abha_user.get('id')}")
            return abha_user
        
        raise credentials_exception
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise credentials_exception

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current active user with additional checks"""
    
    # Check if user is active
    if not current_user.get("active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user

# Dependency for optional authentication
async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """Optional authentication - returns user if token present, None otherwise"""
    
    if not credentials:
        return None
    
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None

# Permission checking
def require_permission(permission: str):
    """Decorator to check specific permissions"""
    def permission_checker(current_user: dict = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        if permission not in user_permissions and "admin" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission {permission} required"
            )
        return current_user
    return permission_checker