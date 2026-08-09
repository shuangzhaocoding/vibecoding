# -*- coding: utf-8 -*-
"""站内通知。"""
from tortoise import fields
from tortoise.models import Model


class Notification(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="notifications")
    actor = fields.ForeignKeyField("models.User", related_name="acted_notifications", null=True)
    type = fields.CharField(max_length=32)  # project_like / project_favorite / project_comment / comment_reply
    project = fields.ForeignKeyField("models.Project", related_name="notifications", null=True)
    comment = fields.ForeignKeyField("models.ProjectComment", related_name="notifications", null=True)
    title = fields.CharField(max_length=200)
    body = fields.CharField(max_length=500, default="")
    link = fields.CharField(max_length=255, default="")
    is_read = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "notifications"
        ordering = ["-id"]
