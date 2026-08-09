# -*- coding: utf-8 -*-
"""用户、角色、权限模型。"""
from tortoise import fields
from tortoise.models import Model


class Permission(Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=64, unique=True)
    name = fields.CharField(max_length=128)
    group = fields.CharField(max_length=64)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "permissions"


class Role(Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=64, unique=True)
    name = fields.CharField(max_length=128)
    data_scope = fields.CharField(max_length=32, default="reported")
    is_system = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    permissions = fields.ManyToManyField(
        "models.Permission", related_name="roles", through="role_permissions"
    )

    class Meta:
        table = "roles"


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=64, unique=True)
    email = fields.CharField(max_length=128, unique=True)
    password_hash = fields.CharField(max_length=255)
    display_name = fields.CharField(max_length=128)
    avatar_url = fields.CharField(max_length=512, default="")
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    roles = fields.ManyToManyField("models.Role", related_name="users", through="user_roles")
    permissions = fields.ManyToManyField(
        "models.Permission", related_name="extra_users", through="user_permissions"
    )

    class Meta:
        table = "users"


class EmailCode(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=128, index=True)
    code = fields.CharField(max_length=16)
    scene = fields.CharField(max_length=32, default="register")
    expire_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "email_codes"
