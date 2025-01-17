import uuid

from fastapi_users import schemas
from typing import Optional
from pydantic import Field

# class UserRead(schemas.BaseUser[uuid.UUID]):
#     pass

class UserRead(schemas.BaseUser[int]):
    corp_userid: Optional[str]
    full_name: Optional[str]
    pass

class UserCreate(schemas.BaseUserCreate):
    corp_userid: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    pass

class UserUpdate(schemas.BaseUserUpdate):
    corp_userid: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    pass