from pydantic import BaseModel, Field, EmailStr
import typing


class UserUpdateSchema(BaseModel):
    nickname: typing.Optional[str]
    password: typing.Optional[str] = Field(alias="password")

class UserBaseSchema(BaseModel):
    email: EmailStr
    nickname: str

class CreateUserSchema(UserBaseSchema):
    password: str = Field(alias="password")

class UserSchema(UserBaseSchema):
    id: int
    is_active: bool = Field(default=False)
    group_id: int

    class Config:
        from_attributes = True