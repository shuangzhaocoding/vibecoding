# -*- coding: utf-8 -*-
"""作品举报。"""
from tortoise import fields
from tortoise.models import Model


class ProjectReport(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="reports")
    reporter = fields.ForeignKeyField("models.User", related_name="reports")
    reason = fields.CharField(max_length=32)  # spam / abuse / copyright / inappropriate / other
    detail = fields.CharField(max_length=500, default="")
    status = fields.CharField(max_length=32, default="pending")  # pending / ignored / resolved
    resolver = fields.ForeignKeyField("models.User", related_name="resolved_reports", null=True)
    resolve_note = fields.CharField(max_length=500, default="")
    resolved_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "project_reports"
        ordering = ["-id"]
