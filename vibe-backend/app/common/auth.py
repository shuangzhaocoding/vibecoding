# -*- coding: utf-8 -*-
"""鉴权依赖：当前用户、可选用户、权限校验。"""
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models import Role, User
from app.schema import AuthException, PermissionException
from app.utils.security import decode_access_token

security = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    user: User
    current_role: Role
    permission_codes: set[str]

    @property
    def id(self) -> int:
        return self.user.id

    @property
    def data_scope(self) -> str:
        return self.current_role.data_scope

    def has_perm(self, code: str) -> bool:
        return code in self.permission_codes


async def _load_effective_permissions(user: User, role: Role) -> set[str]:
    role_perms = await role.permissions.all()
    user_perms = await user.permissions.all()
    return {p.code for p in role_perms} | {p.code for p in user_perms}


async def _resolve_user(
    credentials: Optional[HTTPAuthorizationCredentials],
) -> Optional[CurrentUser]:
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        return None

    user_id = payload.get("sub")
    role_id = payload.get("current_role_id")
    if not user_id or not role_id:
        return None

    user = await User.get_or_none(id=int(user_id))
    if not user or not user.is_active:
        return None

    role = await Role.get_or_none(id=int(role_id))
    if not role:
        return None

    linked = await user.roles.filter(id=role.id).exists()
    if not linked:
        return None

    perms = await _load_effective_permissions(user, role)
    return CurrentUser(user=user, current_role=role, permission_codes=perms)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> CurrentUser:
    current = await _resolve_user(credentials)
    if not current:
        if not credentials or not credentials.credentials:
            raise AuthException(message="missing token", error_code="AUTH_MISSING_TOKEN")
        raise AuthException(message="invalid token", error_code="AUTH_INVALID_TOKEN")
    return current


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[CurrentUser]:
    return await _resolve_user(credentials)


class PermissionChecking:
    """路由级权限点校验。"""

    def __init__(self, *codes: str, require_all: bool = True):
        self.codes = codes
        self.require_all = require_all

    async def __call__(self, current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not self.codes:
            return current
        if self.require_all:
            missing = [c for c in self.codes if c not in current.permission_codes]
            if missing:
                raise PermissionException(
                    message="permission denied",
                    detail={"missing": missing},
                    error_code="PERMISSION_DENIED",
                )
        else:
            if not any(c in current.permission_codes for c in self.codes):
                raise PermissionException(error_code="PERMISSION_DENIED")
        return current
