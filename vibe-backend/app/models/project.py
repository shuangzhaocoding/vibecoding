# -*- coding: utf-8 -*-
"""作品、点赞、收藏、评论模型。"""
from tortoise import fields
from tortoise.models import Model


class Project(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    cover_url = fields.CharField(max_length=512, null=True)
    summary = fields.CharField(max_length=500, null=True)
    description = fields.TextField(null=True)
    site_url = fields.CharField(max_length=512, null=True)
    tags = fields.JSONField(default=list)
    status = fields.CharField(max_length=32, default="published")  # draft/published/hidden
    author = fields.ForeignKeyField("models.User", related_name="projects")
    view_count = fields.IntField(default=0)
    like_count = fields.IntField(default=0)
    favorite_count = fields.IntField(default=0)
    comment_count = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "projects"


class ProjectLike(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="likes")
    project = fields.ForeignKeyField("models.Project", related_name="likes")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "project_likes"
        unique_together = (("user", "project"),)


class ProjectFavorite(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="favorites")
    project = fields.ForeignKeyField("models.Project", related_name="favorites")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "project_favorites"
        unique_together = (("user", "project"),)


class ProjectComment(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="comments")
    user = fields.ForeignKeyField("models.User", related_name="comments")
    content = fields.TextField()
    parent = fields.ForeignKeyField(
        "models.ProjectComment", related_name="replies", null=True
    )
    is_deleted = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "project_comments"
