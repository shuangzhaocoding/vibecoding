# -*- coding: utf-8 -*-
"""系统管理 Schema。"""
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6)
    display_name: str
    role_ids: List[int] = []
    is_active: bool = True


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    role_ids: Optional[List[int]] = None


class RoleCreate(BaseModel):
    code: str
    name: str
    # 预留字段：当前业务未按 data_scope 过滤，仅持久化供后续扩展
    data_scope: str = "reported"


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    data_scope: Optional[str] = None


class PermissionAssign(BaseModel):
    permission_ids: List[int]


class PermissionCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    group: str = Field(min_length=1, max_length=64)


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    group: Optional[str] = Field(default=None, min_length=1, max_length=64)
