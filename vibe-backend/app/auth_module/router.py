# -*- coding: utf-8 -*-
"""认证路由：验证码、注册、登录、登出、切角色、当前用户。"""
from fastapi import APIRouter, Depends

from app.auth_module.schema import (
    LoginBody,
    LoginResult,
    RegisterBody,
    RoleBrief,
    SendCodeBody,
    SwitchRoleBody,
    UserBrief,
)
from app.common.auth import CurrentUser, _load_effective_permissions, get_current_user
from app.models import Role, User
from app.schema import AuthException, BaseAppException, ResponseSuccess
from app.utils.email import create_and_send_register_code, verify_register_code
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


async def _build_login_result(user: User, role: Role) -> LoginResult:
    roles = await user.roles.all()
    perms = await _load_effective_permissions(user, role)
    token = create_access_token(
        {"sub": str(user.id), "current_role_id": role.id, "username": user.username}
    )
    return LoginResult(
        access_token=token,
        user=UserBrief.model_validate(user),
        roles=[RoleBrief.model_validate(r) for r in roles],
        current_role=RoleBrief.model_validate(role),
        permissions=sorted(perms),
    )


@router.post("/send-code", summary="发送注册验证码")
async def send_code(body: SendCodeBody):
    email = body.email.lower()
    if await User.filter(email=email).exists():
        raise BaseAppException(message="email exists", error_code="EMAIL_EXISTS")
    await create_and_send_register_code(email)
    return ResponseSuccess(data=True)


@router.post("/register", summary="邮箱验证码注册")
async def register(body: RegisterBody):
    email = body.email.lower()
    username = body.username.strip()
    if await User.filter(username=username).exists():
        raise BaseAppException(message="username exists", error_code="USER_EXISTS")
    if await User.filter(email=email).exists():
        raise BaseAppException(message="email exists", error_code="EMAIL_EXISTS")
    if not await verify_register_code(email, body.code.strip()):
        raise BaseAppException(message="invalid code", error_code="EMAIL_CODE_INVALID")

    role = await Role.get_or_none(code="creator")
    if not role:
        raise BaseAppException(message="default role missing", error_code="ROLE_NOT_FOUND")

    user = await User.create(
        username=username,
        email=email,
        password_hash=hash_password(body.password),
        display_name=(body.display_name or username).strip(),
        is_active=True,
    )
    await user.roles.add(role)
    data = await _build_login_result(user, role)
    return ResponseSuccess(data=data.model_dump())


@router.post("/login", summary="登录")
async def login(body: LoginBody):
    user = await User.get_or_none(username=body.username)
    if not user:
        user = await User.get_or_none(email=body.username.lower())
    if not user or not verify_password(body.password, user.password_hash):
        raise AuthException(message="invalid credentials", error_code="AUTH_INVALID_CREDENTIALS")
    if not user.is_active:
        raise AuthException(message="user inactive", error_code="AUTH_USER_INACTIVE")
    roles = await user.roles.all()
    if not roles:
        raise AuthException(message="no roles", error_code="AUTH_NO_ROLES")
    role = roles[0]
    data = await _build_login_result(user, role)
    return ResponseSuccess(data=data.model_dump())


@router.post("/logout", summary="退出登录")
async def logout(_: CurrentUser = Depends(get_current_user)):
    return ResponseSuccess(data=True)


@router.post("/switch-role", summary="切换当前角色")
async def switch_role(body: SwitchRoleBody, current: CurrentUser = Depends(get_current_user)):
    role = await Role.get_or_none(id=body.role_id)
    if not role:
        raise AuthException(message="role not found", error_code="AUTH_ROLE_NOT_FOUND")
    linked = await current.user.roles.filter(id=role.id).exists()
    if not linked:
        raise AuthException(message="role not assigned", error_code="AUTH_ROLE_NOT_ASSIGNED")
    data = await _build_login_result(current.user, role)
    return ResponseSuccess(data=data.model_dump())


@router.get("/me", summary="当前用户信息")
async def me(current: CurrentUser = Depends(get_current_user)):
    roles = await current.user.roles.all()
    data = {
        "user": UserBrief.model_validate(current.user).model_dump(),
        "roles": [RoleBrief.model_validate(r).model_dump() for r in roles],
        "current_role": RoleBrief.model_validate(current.current_role).model_dump(),
        "permissions": sorted(current.permission_codes),
    }
    return ResponseSuccess(data=data)
