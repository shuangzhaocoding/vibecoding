# -*- coding: utf-8 -*-
"""公开作者主页与站内通知。"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.auth import CurrentUser, get_current_user, get_optional_user
from app.models import Notification, Project, User
from app.project_module.router import _project_dict, popularity
from app.schema import NotFoundException, ResponseSuccess

router = APIRouter(tags=["users"])


def _author_public(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": getattr(user, "avatar_url", "") or "",
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def _notif_dict(n: Notification) -> dict:
    actor = None
    if n.actor:
        actor = {
            "id": n.actor.id,
            "username": n.actor.username,
            "display_name": n.actor.display_name,
            "avatar_url": getattr(n.actor, "avatar_url", "") or "",
        }
    return {
        "id": n.id,
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "link": n.link,
        "is_read": n.is_read,
        "project_id": n.project_id,
        "comment_id": n.comment_id,
        "actor": actor,
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }


@router.get("/authors/{user_id}", summary="作者公开主页")
async def get_author(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    current: Optional[CurrentUser] = Depends(get_optional_user),
):
    user = await User.get_or_none(id=user_id, is_active=True)
    if not user:
        raise NotFoundException(error_code="USER_NOT_FOUND")

    qs = Project.filter(author_id=user_id, status="published").order_by("-created_at", "-id")
    total = await qs.count()
    projects = await qs.offset((page - 1) * page_size).limit(page_size).prefetch_related("author")
    items = [await _project_dict(p, current) for p in projects]

    all_published = await Project.filter(author_id=user_id, status="published").only(
        "like_count", "favorite_count", "comment_count", "view_count"
    )
    stats = {
        "project_count": total,
        "like_count": sum(p.like_count for p in all_published),
        "favorite_count": sum(p.favorite_count for p in all_published),
        "comment_count": sum(p.comment_count for p in all_published),
        "view_count": sum(p.view_count for p in all_published),
        "popularity": sum(popularity(p) for p in all_published),
    }
    return ResponseSuccess(
        data={
            "author": _author_public(user),
            "stats": stats,
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/notifications", summary="通知列表")
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    unread_only: bool = False,
    current: CurrentUser = Depends(get_current_user),
):
    qs = Notification.filter(user_id=current.id)
    if unread_only:
        qs = qs.filter(is_read=False)
    qs = qs.order_by("-id")
    total = await qs.count()
    rows = await qs.offset((page - 1) * page_size).limit(page_size).prefetch_related("actor")
    return ResponseSuccess(
        data={
            "items": [_notif_dict(n) for n in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/notifications/unread-count", summary="未读通知数")
async def unread_count(current: CurrentUser = Depends(get_current_user)):
    count = await Notification.filter(user_id=current.id, is_read=False).count()
    return ResponseSuccess(data={"count": count})


@router.post("/notifications/read-all", summary="全部标为已读")
async def read_all(current: CurrentUser = Depends(get_current_user)):
    await Notification.filter(user_id=current.id, is_read=False).update(is_read=True)
    return ResponseSuccess(data=True)


@router.post("/notifications/{notification_id}/read", summary="单条标为已读")
async def read_one(notification_id: int, current: CurrentUser = Depends(get_current_user)):
    row = await Notification.get_or_none(id=notification_id, user_id=current.id)
    if not row:
        raise NotFoundException(error_code="NOT_FOUND")
    if not row.is_read:
        row.is_read = True
        await row.save()
    return ResponseSuccess(data=True)

