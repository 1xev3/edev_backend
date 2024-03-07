from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import jwt, logging

from . import schemas


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> schemas.TokenData:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            
            payload = self.getpayload(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=403, detail="Bad token")
            
            return payload
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def getpayload(self, jwtoken: str) -> schemas.TokenData:
        try:
            return schemas.TokenData(**jwt.decode(jwtoken, options={"verify_signature": False}))
        except Exception as E:
            logging.error(E)
            return None