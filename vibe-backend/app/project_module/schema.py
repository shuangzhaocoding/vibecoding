# -*- coding: utf-8 -*-
"""作品模块 Schema。"""
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    cover_url: Optional[str] = None
    summary: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    site_url: Optional[str] = None
    tags: List[str] = []
    status: str = "published"


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    cover_url: Optional[str] = None
    summary: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    site_url: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    parent_id: Optional[int] = None
