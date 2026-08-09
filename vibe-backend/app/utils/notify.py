# -*- coding: utf-8 -*-
"""创建站内通知（忽略自己对自己的操作）。"""
from __future__ import annotations

from typing import Optional

from app.models import Notification, User


async def create_notification(
    *,
    user_id: int,
    actor_id: Optional[int],
    type: str,
    title: str,
    body: str = "",
    link: str = "",
    project_id: Optional[int] = None,
    comment_id: Optional[int] = None,
) -> None:
    if not user_id:
        return
    if actor_id and actor_id == user_id:
        return
    actor_ok = True
    if actor_id:
        actor_ok = await User.filter(id=actor_id, is_active=True).exists()
    if not actor_ok:
        actor_id = None
    await Notification.create(
        user_id=user_id,
        actor_id=actor_id,
        type=type,
        title=title[:200],
        body=(body or "")[:500],
        link=(link or "")[:255],
        project_id=project_id,
        comment_id=comment_id,
        is_read=False,
    )
