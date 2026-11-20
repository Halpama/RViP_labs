import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> str | None:
    if os.getenv("AUTH_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        return None
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("JWT_SECRET", "local-development-secret"),
            algorithms=["HS256"],
        )
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token") from error
    if not isinstance(payload.get("sub"), str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return payload["sub"]
