# -*- coding: utf-8 -*-
"""作品：列表、详情、发布、互动、排行、评论。"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from tortoise import connections
from tortoise.expressions import F, Q, RawSQL

from app.common.auth import CurrentUser, PermissionChecking, get_current_user, get_optional_user
from app.models import (
    Notification,
    Project,
    ProjectComment,
    ProjectFavorite,
    ProjectLike,
    ProjectReport,
    User,
)
from app.project_module.schema import CommentCreate, ProjectCreate, ProjectUpdate, ReportCreate, ReportResolve
from app.schema import BaseAppException, NotFoundException, PermissionException, ResponseSuccess
from app.utils.notify import create_notification
from app.utils.rate_limit import check_rate_limit, seen_recently
from app.utils.request_meta import client_ip

router = APIRouter(prefix="/projects", tags=["projects"])

VALID_STATUS = {"draft", "published", "hidden"}
VALID_REPORT_REASONS = {"spam", "abuse", "copyright", "inappropriate", "other"}
VALID_REPORT_ACTIONS = {"ignore", "hide", "delete"}
VIEW_DEDUPE_SECONDS = 6 * 60 * 60


def popularity(p: Project) -> int:
    return p.like_count * 3 + p.favorite_count * 2 + p.comment_count * 2 + p.view_count


def _author_brief(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": getattr(user, "avatar_url", "") or "",
    }


async def _project_dict(
    p: Project,
    current: Optional[CurrentUser] = None,
    *,
    include_description: bool = False,
) -> dict:
    await p.fetch_related("author")
    liked = False
    favorited = False
    if current:
        liked = await ProjectLike.filter(user_id=current.id, project_id=p.id).exists()
        favorited = await ProjectFavorite.filter(user_id=current.id, project_id=p.id).exists()
    data = {
        "id": p.id,
        "title": p.title,
        "cover_url": p.cover_url,
        "summary": p.summary,
        "site_url": p.site_url,
        "tags": p.tags or [],
        "status": p.status,
        "author": _author_brief(p.author),
        "view_count": p.view_count,
        "like_count": p.like_count,
        "favorite_count": p.favorite_count,
        "comment_count": p.comment_count,
        "popularity": popularity(p),
        "liked": liked,
        "favorited": favorited,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
    if include_description:
        data["description"] = p.description
    return data


def _can_manage(project: Project, current: CurrentUser) -> bool:
    return current.has_perm("project:manage") or project.author_id == current.id


async def _purge_project(project_id: int) -> None:
    """删除作品关联数据（点赞/收藏/评论/通知/举报）。"""
    await ProjectLike.filter(project_id=project_id).delete()
    await ProjectFavorite.filter(project_id=project_id).delete()
    await ProjectComment.filter(project_id=project_id).delete()
    await Notification.filter(project_id=project_id).delete()
    await ProjectReport.filter(project_id=project_id).delete()


async def _ids_with_tag(tag: str) -> list[int]:
    """MySQL JSON_CONTAINS 精确匹配标签。"""
    tag = (tag or "").strip()
    if not tag:
        return []
    conn = connections.get("default")
    rows = await conn.execute_query_dict(
        "SELECT id FROM projects WHERE JSON_CONTAINS(COALESCE(tags, JSON_ARRAY()), %s)",
        [json.dumps(tag)],
    )
    return [int(r["id"]) for r in rows]


def _apply_sort(qs, sort: str):
    if sort == "likes":
        return qs.order_by("-like_count", "-id")
    if sort == "popular":
        return qs.annotate(
            pop_score=RawSQL("(like_count * 3 + favorite_count * 2 + comment_count * 2 + view_count)")
        ).order_by("-pop_score", "-id")
    return qs.order_by("-created_at", "-id")


@router.get("/tags", summary="热门标签")
async def list_tags(limit: int = Query(40, ge=1, le=100)):
    projects = await Project.filter(status="published").only("tags").limit(800)
    counter: Counter[str] = Counter()
    for p in projects:
        for tag in p.tags or []:
            name = str(tag).strip()
            if name:
                counter[name] += 1
    data = [{"name": name, "count": count} for name, count in counter.most_common(limit)]
    return ResponseSuccess(data=data)


@router.get("", summary="作品列表")
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
    status: Optional[str] = None,
    sort: str = Query("newest", pattern="^(newest|popular|likes)$"),
    mine: bool = False,
    favorites: bool = False,
    liked: bool = False,
    current: Optional[CurrentUser] = Depends(get_optional_user),
):
    qs = Project.all()

    if mine:
        if not current:
            raise PermissionException(error_code="AUTH_MISSING_TOKEN")
        qs = qs.filter(author_id=current.id)
        if status:
            if status not in VALID_STATUS:
                raise BaseAppException(message="invalid status", error_code="INVALID_STATUS")
            qs = qs.filter(status=status)
    elif favorites:
        if not current:
            raise PermissionException(error_code="AUTH_MISSING_TOKEN")
        fav_ids = await ProjectFavorite.filter(user_id=current.id).values_list("project_id", flat=True)
        qs = qs.filter(id__in=list(fav_ids) or [-1], status="published")
    elif liked:
        if not current:
            raise PermissionException(error_code="AUTH_MISSING_TOKEN")
        like_ids = await ProjectLike.filter(user_id=current.id).values_list("project_id", flat=True)
        qs = qs.filter(id__in=list(like_ids) or [-1], status="published")
    else:
        if current and current.has_perm("project:manage") and status:
            if status not in VALID_STATUS:
                raise BaseAppException(message="invalid status", error_code="INVALID_STATUS")
            qs = qs.filter(status=status)
        elif not (current and current.has_perm("project:manage")):
            qs = qs.filter(status="published")

    kw = (keyword or "").strip()
    if kw:
        qs = qs.filter(Q(title__icontains=kw) | Q(summary__icontains=kw))

    tag_name = (tag or "").strip()
    if tag_name:
        tag_ids = await _ids_with_tag(tag_name)
        if not tag_ids:
            return ResponseSuccess(data={"items": [], "total": 0, "page": page, "page_size": page_size})
        qs = qs.filter(id__in=tag_ids)

    qs = _apply_sort(qs, sort)
    total = await qs.count()
    offset = (page - 1) * page_size
    projects = await qs.offset(offset).limit(page_size).prefetch_related("author")
    items = [await _project_dict(p, current) for p in projects]
    return ResponseSuccess(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/reports", summary="举报审核列表")
async def list_reports(
    status: Optional[str] = Query(default="pending"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current: CurrentUser = Depends(PermissionChecking("project:manage")),
):
    qs = ProjectReport.all().prefetch_related("project", "reporter", "resolver")
    if status and status != "all":
        qs = qs.filter(status=status)
    total = await qs.count()
    rows = await qs.offset((page - 1) * page_size).limit(page_size)
    items = []
    for r in rows:
        items.append(
            {
                "id": r.id,
                "reason": r.reason,
                "detail": r.detail,
                "status": r.status,
                "resolve_note": r.resolve_note,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
                "project": {
                    "id": r.project.id,
                    "title": r.project.title,
                    "status": r.project.status,
                    "cover_url": r.project.cover_url,
                }
                if r.project
                else None,
                "reporter": {
                    "id": r.reporter.id,
                    "username": r.reporter.username,
                    "display_name": r.reporter.display_name,
                }
                if r.reporter
                else None,
                "resolver": {
                    "id": r.resolver.id,
                    "display_name": r.resolver.display_name,
                }
                if r.resolver
                else None,
            }
        )
    return ResponseSuccess(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("/reports/{report_id}/resolve", summary="处理举报")
async def resolve_report(
    report_id: int,
    body: ReportResolve,
    current: CurrentUser = Depends(PermissionChecking("project:manage")),
):
    action = (body.action or "").strip().lower()
    if action not in VALID_REPORT_ACTIONS:
        raise BaseAppException(message="invalid action", error_code="INVALID_REPORT_ACTION")

    report = await ProjectReport.get_or_none(id=report_id).prefetch_related("project")
    if not report:
        raise NotFoundException(error_code="REPORT_NOT_FOUND")
    if report.status != "pending":
        raise BaseAppException(message="report already handled", error_code="REPORT_ALREADY_RESOLVED")

    project = report.project
    project_id = project.id if project else None
    note = (body.note or "").strip()
    now = datetime.now(timezone.utc)

    if action == "delete":
        if project_id:
            await ProjectReport.filter(project_id=project_id, status="pending").update(
                status="resolved",
                resolver_id=current.id,
                resolve_note=note or "closed after delete",
                resolved_at=now,
            )
            await _purge_project(project_id)
            await project.delete()
        return ResponseSuccess(
            data={"id": report_id, "status": "resolved", "action": action, "project_status": None}
        )

    if action == "hide":
        if not project:
            raise NotFoundException(error_code="PROJECT_NOT_FOUND")
        project.status = "hidden"
        await project.save(update_fields=["status", "updated_at"])
        report.status = "resolved"
        project_status = "hidden"
    else:
        report.status = "ignored"
        project_status = project.status if project else None

    report.resolver_id = current.id
    report.resolve_note = note
    report.resolved_at = now
    await report.save()

    if action == "hide" and project_id:
        await ProjectReport.filter(project_id=project_id, status="pending").exclude(id=report.id).update(
            status="resolved",
            resolver_id=current.id,
            resolve_note=note or "auto-closed after hide",
            resolved_at=now,
        )

    return ResponseSuccess(
        data={
            "id": report.id,
            "status": report.status,
            "action": action,
            "project_status": project_status,
        }
    )


@router.get("/ranking", summary="人气排行")
async def ranking(
    limit: int = Query(20, ge=1, le=100),
    current: Optional[CurrentUser] = Depends(get_optional_user),
):
    qs = (
        Project.filter(status="published")
        .annotate(
            pop_score=RawSQL("(like_count * 3 + favorite_count * 2 + comment_count * 2 + view_count)")
        )
        .order_by("-pop_score", "-id")
        .limit(limit)
        .prefetch_related("author")
    )
    projects = await qs
    items = []
    for idx, p in enumerate(projects, start=1):
        data = await _project_dict(p, current)
        data["rank"] = idx
        items.append(data)
    return ResponseSuccess(data=items)


@router.get("/{project_id}", summary="作品详情")
async def get_project(
    project_id: int,
    request: Request,
    current: Optional[CurrentUser] = Depends(get_optional_user),
):
    project = await Project.get_or_none(id=project_id).prefetch_related("author")
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    if project.status != "published":
        if not current or not _can_manage(project, current):
            raise NotFoundException(error_code="PROJECT_NOT_FOUND")

    # 同一 IP 6 小时内对同一作品只计一次浏览
    ip = client_ip(request)
    view_key = f"view:{project_id}:{ip}"
    if project.status == "published" and not seen_recently(view_key, window_seconds=VIEW_DEDUPE_SECONDS):
        await Project.filter(id=project_id).update(view_count=F("view_count") + 1)
        await project.refresh_from_db()

    return ResponseSuccess(data=await _project_dict(project, current, include_description=True))


@router.post("", summary="发布作品")
async def create_project(
    body: ProjectCreate,
    current: CurrentUser = Depends(PermissionChecking("project:create")),
):
    if body.status not in VALID_STATUS:
        raise BaseAppException(message="invalid status", error_code="INVALID_STATUS")
    project = await Project.create(
        title=body.title.strip(),
        cover_url=body.cover_url,
        summary=body.summary,
        description=body.description,
        site_url=body.site_url,
        tags=body.tags or [],
        status=body.status,
        author_id=current.id,
    )
    await project.fetch_related("author")
    return ResponseSuccess(data=await _project_dict(project, current, include_description=True))


@router.patch("/{project_id}", summary="更新作品")
async def update_project(
    project_id: int,
    body: ProjectUpdate,
    current: CurrentUser = Depends(PermissionChecking("project:update", "project:manage", require_all=False)),
):
    project = await Project.get_or_none(id=project_id)
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    if not _can_manage(project, current):
        raise PermissionException(error_code="PERMISSION_DENIED")
    if body.status is not None and body.status not in VALID_STATUS:
        raise BaseAppException(message="invalid status", error_code="INVALID_STATUS")

    for field in ("title", "cover_url", "summary", "description", "site_url", "tags", "status"):
        value = getattr(body, field)
        if value is not None:
            if field == "title":
                value = value.strip()
            setattr(project, field, value)
    await project.save()
    await project.fetch_related("author")
    return ResponseSuccess(data=await _project_dict(project, current, include_description=True))


@router.delete("/{project_id}", summary="删除作品")
async def delete_project(
    project_id: int,
    current: CurrentUser = Depends(PermissionChecking("project:delete", "project:manage", require_all=False)),
):
    project = await Project.get_or_none(id=project_id)
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    if not _can_manage(project, current):
        raise PermissionException(error_code="PERMISSION_DENIED")
    await _purge_project(project_id)
    await project.delete()
    return ResponseSuccess(data=True)


@router.post("/{project_id}/report", summary="举报作品")
async def report_project(
    project_id: int,
    body: ReportCreate,
    current: CurrentUser = Depends(get_current_user),
):
    reason = (body.reason or "").strip().lower()
    if reason not in VALID_REPORT_REASONS:
        raise BaseAppException(message="invalid reason", error_code="INVALID_REPORT_REASON")

    project = await Project.get_or_none(id=project_id, status="published")
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    if project.author_id == current.id:
        raise BaseAppException(message="cannot report own project", error_code="CANNOT_REPORT_OWN")

    check_rate_limit(f"report:user:{current.id}", limit=10, window_seconds=3600, error_code="REPORT_RATE_LIMITED")

    exists = await ProjectReport.filter(
        project_id=project_id, reporter_id=current.id, status="pending"
    ).exists()
    if exists:
        raise BaseAppException(message="already reported", error_code="ALREADY_REPORTED")

    report = await ProjectReport.create(
        project_id=project_id,
        reporter_id=current.id,
        reason=reason,
        detail=(body.detail or "").strip(),
        status="pending",
    )
    return ResponseSuccess(data={"id": report.id, "status": report.status})


@router.post("/{project_id}/like", summary="点赞")
async def like_project(
    project_id: int,
    current: CurrentUser = Depends(PermissionChecking("project:interact")),
):
    project = await Project.get_or_none(id=project_id, status="published")
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    created = await ProjectLike.get_or_none(user_id=current.id, project_id=project_id)
    if not created:
        await ProjectLike.create(user_id=current.id, project_id=project_id)
        await Project.filter(id=project_id).update(like_count=F("like_count") + 1)
        await create_notification(
            user_id=project.author_id,
            actor_id=current.id,
            type="project_like",
            title="有人点赞了你的作品",
            body=project.title,
            link=f"/projects/{project.id}",
            project_id=project.id,
        )
    await project.refresh_from_db()
    return ResponseSuccess(data={"liked": True, "like_count": project.like_count})


@router.delete("/{project_id}/like", summary="取消点赞")
async def unlike_project(
    project_id: int,
    current: CurrentUser = Depends(PermissionChecking("project:interact")),
):
    project = await Project.get_or_none(id=project_id)
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    row = await ProjectLike.get_or_none(user_id=current.id, project_id=project_id)
    if row:
        await row.delete()
        if project.like_count > 0:
            await Project.filter(id=project_id).update(like_count=F("like_count") - 1)
    await project.refresh_from_db()
    return ResponseSuccess(data={"liked": False, "like_count": project.like_count})


@router.post("/{project_id}/favorite", summary="收藏")
async def favorite_project(
    project_id: int,
    current: CurrentUser = Depends(PermissionChecking("project:interact")),
):
    project = await Project.get_or_none(id=project_id, status="published")
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    created = await ProjectFavorite.get_or_none(user_id=current.id, project_id=project_id)
    if not created:
        await ProjectFavorite.create(user_id=current.id, project_id=project_id)
        await Project.filter(id=project_id).update(favorite_count=F("favorite_count") + 1)
        await create_notification(
            user_id=project.author_id,
            actor_id=current.id,
            type="project_favorite",
            title="有人收藏了你的作品",
            body=project.title,
            link=f"/projects/{project.id}",
            project_id=project.id,
        )
    await project.refresh_from_db()
    return ResponseSuccess(data={"favorited": True, "favorite_count": project.favorite_count})


@router.delete("/{project_id}/favorite", summary="取消收藏")
async def unfavorite_project(
    project_id: int,
    current: CurrentUser = Depends(PermissionChecking("project:interact")),
):
    project = await Project.get_or_none(id=project_id)
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    row = await ProjectFavorite.get_or_none(user_id=current.id, project_id=project_id)
    if row:
        await row.delete()
        if project.favorite_count > 0:
            await Project.filter(id=project_id).update(favorite_count=F("favorite_count") - 1)
    await project.refresh_from_db()
    return ResponseSuccess(data={"favorited": False, "favorite_count": project.favorite_count})


def _comment_node(c: ProjectComment, reply_to: Optional[dict] = None) -> dict:
    return {
        "id": c.id,
        "content": c.content,
        "parent_id": c.parent_id,
        "user": _author_brief(c.user),
        "reply_to": reply_to,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "children": [],
    }


def _build_comment_tree(comments: list[ProjectComment]) -> list[dict]:
    nodes: dict[int, dict] = {}
    for c in comments:
        nodes[c.id] = _comment_node(c)

    roots: list[dict] = []
    for c in comments:
        node = nodes[c.id]
        if c.parent_id and c.parent_id in nodes:
            parent = nodes[c.parent_id]
            node["reply_to"] = parent["user"]
            parent["children"].append(node)
        else:
            roots.append(node)

    roots.sort(key=lambda x: x["created_at"] or "", reverse=True)
    return roots


@router.get("/{project_id}/comments", summary="评论树")
async def list_comments(project_id: int):
    project = await Project.get_or_none(id=project_id)
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    comments = (
        await ProjectComment.filter(project_id=project_id, is_deleted=False)
        .order_by("created_at")
        .prefetch_related("user")
    )
    tree = _build_comment_tree(list(comments))
    return ResponseSuccess(data={"items": tree, "total": len(comments)})


@router.post("/{project_id}/comments", summary="发表评论")
async def create_comment(
    project_id: int,
    body: CommentCreate,
    current: CurrentUser = Depends(PermissionChecking("project:interact")),
):
    project = await Project.get_or_none(id=project_id, status="published")
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    content = (body.content or "").strip()
    if not content or content in ("<p><br></p>", "<p></p>"):
        raise BaseAppException(message="empty comment", error_code="COMMENT_EMPTY")

    reply_to = None
    parent = None
    if body.parent_id:
        parent = await ProjectComment.get_or_none(
            id=body.parent_id, project_id=project_id, is_deleted=False
        ).prefetch_related("user")
        if not parent:
            raise NotFoundException(error_code="COMMENT_NOT_FOUND")
        reply_to = _author_brief(parent.user)

    comment = await ProjectComment.create(
        project_id=project_id,
        user_id=current.id,
        content=content,
        parent_id=body.parent_id,
    )
    await Project.filter(id=project_id).update(comment_count=F("comment_count") + 1)
    await comment.fetch_related("user")

    # 纯文本摘要用于通知正文
    plain = content.replace("<", " ").replace(">", " ")
    plain = " ".join(plain.split())[:80]

    if parent:
        await create_notification(
            user_id=parent.user_id,
            actor_id=current.id,
            type="comment_reply",
            title="有人回复了你的评论",
            body=plain or project.title,
            link=f"/projects/{project.id}",
            project_id=project.id,
            comment_id=comment.id,
        )
    else:
        await create_notification(
            user_id=project.author_id,
            actor_id=current.id,
            type="project_comment",
            title="有人评论了你的作品",
            body=plain or project.title,
            link=f"/projects/{project.id}",
            project_id=project.id,
            comment_id=comment.id,
        )

    data = _comment_node(comment, reply_to=reply_to)
    return ResponseSuccess(data=data)


@router.delete("/{project_id}/comments/{comment_id}", summary="删除评论")
async def delete_comment(
    project_id: int,
    comment_id: int,
    current: CurrentUser = Depends(get_current_user),
):
    project = await Project.get_or_none(id=project_id)
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")

    comment = await ProjectComment.get_or_none(
        id=comment_id, project_id=project_id, is_deleted=False
    )
    if not comment:
        raise NotFoundException(error_code="COMMENT_NOT_FOUND")

    can_delete = (
        comment.user_id == current.id
        or project.author_id == current.id
        or current.has_perm("project:manage")
    )
    if not can_delete:
        raise PermissionException(error_code="PERMISSION_DENIED")

    # 软删自身及未删除的子孙评论
    all_comments = await ProjectComment.filter(project_id=project_id, is_deleted=False).only("id", "parent_id")
    children_map: dict[int, list[int]] = {}
    for row in all_comments:
        if row.parent_id:
            children_map.setdefault(row.parent_id, []).append(row.id)

    to_delete: list[int] = []
    stack = [comment.id]
    while stack:
        cid = stack.pop()
        to_delete.append(cid)
        stack.extend(children_map.get(cid, []))

    await ProjectComment.filter(id__in=to_delete).update(is_deleted=True)
    dec = len(to_delete)
    new_count = max(0, project.comment_count - dec)
    await Project.filter(id=project_id).update(comment_count=new_count)
    return ResponseSuccess(data={"deleted": dec, "comment_count": new_count})
