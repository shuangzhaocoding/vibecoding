# -*- coding: utf-8 -*-
"""用户 / 角色 / 权限管理路由。"""
from fastapi import APIRouter, Depends, Query

from app.auth_module.schema import RoleBrief, UserBrief
from app.common.auth import CurrentUser, PermissionChecking
from app.models import Permission, Role, User
from app.schema import BaseAppException, NotFoundException, ResponseSuccess
from app.system_module.schema import (
    PermissionAssign,
    PermissionCreate,
    PermissionUpdate,
    RoleCreate,
    RoleUpdate,
    UserCreate,
    UserUpdate,
)
from app.utils.security import hash_password

router = APIRouter(tags=["system"])


def _user_dict(user: User, roles: list[Role] | None = None, perm_ids: list[int] | None = None) -> dict:
    data = UserBrief.model_validate(user).model_dump()
    if roles is not None:
        data["roles"] = [RoleBrief.model_validate(r).model_dump() for r in roles]
    if perm_ids is not None:
        data["permission_ids"] = perm_ids
    return data


@router.get("/users", summary="用户列表")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: CurrentUser = Depends(PermissionChecking("system:user:view")),
):
    total = await User.all().count()
    users = await User.all().offset((page - 1) * page_size).limit(page_size)
    items = []
    for u in users:
        roles = await u.roles.all()
        perms = await u.permissions.all()
        items.append(_user_dict(u, roles, [p.id for p in perms]))
    return ResponseSuccess(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("/users", summary="创建用户")
async def create_user(
    body: UserCreate,
    _: CurrentUser = Depends(PermissionChecking("system:user:manage")),
):
    if await User.filter(username=body.username).exists():
        raise BaseAppException(message="username exists", error_code="USER_EXISTS")
    email = str(body.email).lower()
    if await User.filter(email=email).exists():
        raise BaseAppException(message="email exists", error_code="EMAIL_EXISTS")
    user = await User.create(
        username=body.username,
        email=email,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
        is_active=body.is_active,
    )
    if body.role_ids:
        roles = await Role.filter(id__in=body.role_ids)
        await user.roles.add(*roles)
    roles = await user.roles.all()
    return ResponseSuccess(data=_user_dict(user, roles, []))


@router.patch("/users/{user_id}", summary="更新用户")
async def update_user(
    user_id: int,
    body: UserUpdate,
    _: CurrentUser = Depends(PermissionChecking("system:user:manage")),
):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise NotFoundException(error_code="USER_NOT_FOUND")
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.email is not None:
        email = str(body.email).lower()
        exists = await User.filter(email=email).exclude(id=user.id).exists()
        if exists:
            raise BaseAppException(message="email exists", error_code="EMAIL_EXISTS")
        user.email = email
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.password:
        user.password_hash = hash_password(body.password)
    await user.save()
    if body.role_ids is not None:
        await user.roles.clear()
        roles = await Role.filter(id__in=body.role_ids)
        if roles:
            await user.roles.add(*roles)
    roles = await user.roles.all()
    perms = await user.permissions.all()
    return ResponseSuccess(data=_user_dict(user, roles, [p.id for p in perms]))


@router.put("/users/{user_id}/permissions", summary="覆盖用户附加权限")
async def assign_user_permissions(
    user_id: int,
    body: PermissionAssign,
    _: CurrentUser = Depends(PermissionChecking("system:perm:assign")),
):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise NotFoundException(error_code="USER_NOT_FOUND")
    await user.permissions.clear()
    perms = await Permission.filter(id__in=body.permission_ids)
    if perms:
        await user.permissions.add(*perms)
    return ResponseSuccess(data={"permission_ids": [p.id for p in perms]})


@router.get("/roles", summary="角色列表")
async def list_roles(
    _: CurrentUser = Depends(
        PermissionChecking(
            "system:role:view",
            "system:perm:assign",
            "system:user:manage",
            require_all=False,
        )
    ),
):
    roles = await Role.all()
    items = []
    for r in roles:
        perms = await r.permissions.all()
        item = RoleBrief.model_validate(r).model_dump()
        item["is_system"] = r.is_system
        item["permission_ids"] = [p.id for p in perms]
        items.append(item)
    return ResponseSuccess(data=items)


@router.post("/roles", summary="创建角色")
async def create_role(
    body: RoleCreate,
    _: CurrentUser = Depends(PermissionChecking("system:role:manage")),
):
    if body.data_scope not in ("all", "assigned", "reported"):
        raise BaseAppException(message="invalid data_scope", error_code="INVALID_DATA_SCOPE")
    if await Role.filter(code=body.code).exists():
        raise BaseAppException(message="role exists", error_code="ROLE_EXISTS")
    role = await Role.create(code=body.code, name=body.name, data_scope=body.data_scope, is_system=False)
    item = RoleBrief.model_validate(role).model_dump()
    item["is_system"] = False
    item["permission_ids"] = []
    return ResponseSuccess(data=item)


@router.patch("/roles/{role_id}", summary="更新角色")
async def update_role(
    role_id: int,
    body: RoleUpdate,
    _: CurrentUser = Depends(PermissionChecking("system:role:manage")),
):
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise NotFoundException(error_code="ROLE_NOT_FOUND")
    if body.name is not None:
        role.name = body.name
    if body.data_scope is not None:
        if body.data_scope not in ("all", "assigned", "reported"):
            raise BaseAppException(message="invalid data_scope", error_code="INVALID_DATA_SCOPE")
        role.data_scope = body.data_scope
    await role.save()
    perms = await role.permissions.all()
    item = RoleBrief.model_validate(role).model_dump()
    item["is_system"] = role.is_system
    item["permission_ids"] = [p.id for p in perms]
    return ResponseSuccess(data=item)


@router.delete("/roles/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    _: CurrentUser = Depends(PermissionChecking("system:role:manage")),
):
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise NotFoundException(error_code="ROLE_NOT_FOUND")
    if role.is_system:
        raise BaseAppException(message="system role cannot delete", error_code="SYSTEM_ROLE_PROTECTED")
    await role.delete()
    return ResponseSuccess(data=True)


@router.put("/roles/{role_id}/permissions", summary="覆盖角色权限")
async def assign_role_permissions(
    role_id: int,
    body: PermissionAssign,
    _: CurrentUser = Depends(PermissionChecking("system:perm:assign")),
):
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise NotFoundException(error_code="ROLE_NOT_FOUND")
    await role.permissions.clear()
    perms = await Permission.filter(id__in=body.permission_ids)
    if perms:
        await role.permissions.add(*perms)
    return ResponseSuccess(data={"permission_ids": [p.id for p in perms]})


@router.get("/permissions", summary="权限点列表")
async def list_permissions(
    _: CurrentUser = Depends(
        PermissionChecking(
            "system:role:view",
            "system:perm:assign",
            "system:perm:view",
            "system:perm:manage",
            require_all=False,
        )
    ),
):
    perms = await Permission.all().order_by("group", "id")
    groups: dict[str, list] = {}
    for p in perms:
        groups.setdefault(p.group, []).append(
            {"id": p.id, "code": p.code, "name": p.name, "group": p.group}
        )
    return ResponseSuccess(
        data={
            "items": [{"id": p.id, "code": p.code, "name": p.name, "group": p.group} for p in perms],
            "groups": groups,
        }
    )


@router.post("/permissions", summary="创建权限点")
async def create_permission(
    body: PermissionCreate,
    _: CurrentUser = Depends(PermissionChecking("system:perm:manage")),
):
    code = body.code.strip()
    name = body.name.strip()
    group = body.group.strip()
    if not code or " " in code:
        raise BaseAppException(message="invalid permission code", error_code="INVALID_PERM_CODE")
    if await Permission.filter(code=code).exists():
        raise BaseAppException(message="permission exists", error_code="PERM_EXISTS")
    perm = await Permission.create(code=code, name=name, group=group)
    return ResponseSuccess(data={"id": perm.id, "code": perm.code, "name": perm.name, "group": perm.group})


@router.patch("/permissions/{perm_id}", summary="更新权限点")
async def update_permission(
    perm_id: int,
    body: PermissionUpdate,
    _: CurrentUser = Depends(PermissionChecking("system:perm:manage")),
):
    perm = await Permission.get_or_none(id=perm_id)
    if not perm:
        raise NotFoundException(error_code="PERM_NOT_FOUND")
    if body.name is not None:
        perm.name = body.name.strip()
    if body.group is not None:
        perm.group = body.group.strip()
    await perm.save()
    return ResponseSuccess(data={"id": perm.id, "code": perm.code, "name": perm.name, "group": perm.group})


@router.delete("/permissions/{perm_id}", summary="删除权限点")
async def delete_permission(
    perm_id: int,
    _: CurrentUser = Depends(PermissionChecking("system:perm:manage")),
):
    perm = await Permission.get_or_none(id=perm_id)
    if not perm:
        raise NotFoundException(error_code="PERM_NOT_FOUND")
    await perm.roles.clear()
    await perm.extra_users.clear()
    await perm.delete()
    return ResponseSuccess(data=True)
