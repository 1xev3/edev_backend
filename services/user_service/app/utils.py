from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

class HashContext():
    def __init__(
                self, 
                JWT_SECRET_KEY: str,
                JWT_REFRESH_SECRET_KEY: str,
                ACCESS_TOKEN_EXPIRE_MINUTES=30, # 30 minutes
                REFRESH_TOKEN_EXPIRE_MINUTES=60 * 24 * 7, # 7 days
                ALGORITHM="HS256",
            ):
        self.JWT_SECRET_KEY = JWT_SECRET_KEY
        self.JWT_REFRESH_SECRET_KEY = JWT_REFRESH_SECRET_KEY
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
        self.REFRESH_TOKEN_EXPIRE_MINUTES = REFRESH_TOKEN_EXPIRE_MINUTES
        self.ALGORITHM = ALGORITHM

        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_hashed_password(self, password: str) -> str:
        return self.password_context.hash(password)


    def verify_password(self, password: str, hashed_pass: str) -> bool:
        return self.password_context.verify(password, hashed_pass)


    def create_access_token(self, subject: Union[str, Any], expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, self.JWT_SECRET_KEY, self.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, subject: Union[str, Any], expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, self.JWT_REFRESH_SECRET_KEY, self.ALGORITHM)
        return encoded_jwt