"""
Authentication and security handlers.
"""
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import logging

# Get logger
logger = logging.getLogger("ansible_llm")

# Secret key should be stored securely, not hardcoded
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    logger.warning("SECRET_KEY not set in environment variables. Using an insecure default!")
    SECRET_KEY = "insecurekey_please_set_SECRET_KEY_environment_variable"

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    permissions: Optional[list[str]] = None

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Get the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, permissions=payload.get("permissions", []))
    except JWTError:
        logger.warning("Invalid JWT token attempt")
        raise credentials_exception
    
    user = {"username": token_data.username, "permissions": token_data.permissions}
    return user

def require_permission(permission: str):
    """Decorator to require a specific permission."""
    async def dependency(user: Dict = Depends(get_current_user)):
        if permission not in user.get("permissions", []):
            logger.warning(f"Unauthorized access attempt by {user['username']}: missing {permission} permission")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not enough permissions"
            )
        return user
    return dependency
