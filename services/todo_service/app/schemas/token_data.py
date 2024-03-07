from pydantic import BaseModel, Field

#{'sub': 'onexevs@gmail.com', 'exp': 1709846229, 'group_id': 0}
class TokenData(BaseModel):
    sub: str = Field(title="User email")
    exp: int = Field(title="Token expiry")
    group_id: int = Field(title="User group id")