# -*- coding: utf-8 -*-
"""认证模块 Schema。"""
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class LoginBody(BaseModel):
    username: str
    password: str


class SendCodeBody(BaseModel):
    email: EmailStr


class RegisterBody(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    code: str = Field(min_length=4, max_length=16)
    display_name: Optional[str] = None


class SwitchRoleBody(BaseModel):
    role_id: int


class RoleBrief(BaseModel):
    id: int
    code: str
    name: str
    data_scope: str

    class Config:
        from_attributes = True


class UserBrief(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    is_active: bool

    class Config:
        from_attributes = True


class LoginResult(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBrief
    roles: List[RoleBrief]
    current_role: RoleBrief
    permissions: List[str]
