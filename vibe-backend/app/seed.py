# -*- coding: utf-8 -*-
"""种子数据：权限、角色、管理员。"""
from loguru import logger

from app.config.settings import settings
from app.models import Permission, Role, User
from app.utils.security import hash_password

PERMISSIONS = [
    ("system:user:view", "查看用户", "system"),
    ("system:user:manage", "管理用户", "system"),
    ("system:role:view", "查看角色", "system"),
    ("system:role:manage", "管理角色", "system"),
    ("system:perm:view", "查看权限点", "system"),
    ("system:perm:manage", "管理权限点", "system"),
    ("system:perm:assign", "分配权限", "system"),
    ("project:view", "查看作品", "project"),
    ("project:create", "发布作品", "project"),
    ("project:update", "编辑作品", "project"),
    ("project:delete", "删除作品", "project"),
    ("project:interact", "点赞收藏评论", "project"),
    ("project:manage", "管理全部作品", "project"),
]

ROLE_DEFS = {
    "admin": {
        "name": "管理员",
        "data_scope": "all",
        "is_system": True,
        "perms": [p[0] for p in PERMISSIONS],
    },
    "creator": {
        "name": "创作者",
        "data_scope": "reported",
        "is_system": True,
        "perms": [
            "project:view",
            "project:create",
            "project:update",
            "project:delete",
            "project:interact",
        ],
    },
}


async def _ensure_user_avatar_column() -> None:
    """已有库补充 avatar_url 列（Tortoise generate_schemas 不会 ALTER）。"""
    from tortoise import connections

    conn = connections.get("default")
    rows = await conn.execute_query_dict(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'avatar_url'"
    )
    if rows:
        return
    try:
        await conn.execute_query(
            "ALTER TABLE `users` ADD COLUMN `avatar_url` VARCHAR(512) NOT NULL DEFAULT ''"
        )
        logger.info("added column users.avatar_url")
    except Exception as exc:
        msg = str(exc)
        if "1060" in msg or "Duplicate column" in msg:
            return
        logger.warning(f"ensure avatar_url failed: {exc}")


async def seed_data() -> None:
    await _ensure_user_avatar_column()
    for code, name, group in PERMISSIONS:
        perm = await Permission.get_or_none(code=code)
        if not perm:
            await Permission.create(code=code, name=name, group=group)
            logger.info(f"seeded permission {code}")

    perm_map = {p.code: p for p in await Permission.all()}

    for code, meta in ROLE_DEFS.items():
        role = await Role.get_or_none(code=code)
        if not role:
            role = await Role.create(
                code=code,
                name=meta["name"],
                data_scope=meta["data_scope"],
                is_system=meta["is_system"],
            )
            await role.permissions.add(*[perm_map[c] for c in meta["perms"] if c in perm_map])
            logger.info(f"seeded role {code}")
        else:
            existing = {p.code for p in await role.permissions.all()}
            missing = [perm_map[c] for c in meta["perms"] if c in perm_map and c not in existing]
            if missing:
                await role.permissions.add(*missing)
                logger.info(f"synced role {code} perms: +{[p.code for p in missing]}")

    admin_role = await Role.get(code="admin")
    admin = await User.get_or_none(username="admin")
    if not admin:
        admin = await User.create(
            username="admin",
            email="admin@vibecoding.local",
            password_hash=hash_password(settings.default_password),
            display_name="系统管理员",
            is_active=True,
        )
        await admin.roles.add(admin_role)
        logger.info("seeded admin user")
    else:
        linked = await admin.roles.filter(id=admin_role.id).exists()
        if not linked:
            await admin.roles.add(admin_role)
