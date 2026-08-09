# -*- coding: utf-8 -*-
"""作品：列表、详情、发布、互动、排行、评论。"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from tortoise.expressions import F

from app.common.auth import CurrentUser, PermissionChecking, get_optional_user
from app.models import Project, ProjectComment, ProjectFavorite, ProjectLike, User
from app.project_module.schema import CommentCreate, ProjectCreate, ProjectUpdate
from app.schema import BaseAppException, NotFoundException, PermissionException, ResponseSuccess

router = APIRouter(prefix="/projects", tags=["projects"])

VALID_STATUS = {"draft", "published", "hidden"}


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


@router.get("", summary="作品列表")
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
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
    elif favorites:
        if not current:
            raise PermissionException(error_code="AUTH_MISSING_TOKEN")
        fav_ids = await ProjectFavorite.filter(user_id=current.id).values_list("project_id", flat=True)
        qs = qs.filter(id__in=list(fav_ids), status="published")
    elif liked:
        if not current:
            raise PermissionException(error_code="AUTH_MISSING_TOKEN")
        like_ids = await ProjectLike.filter(user_id=current.id).values_list("project_id", flat=True)
        qs = qs.filter(id__in=list(like_ids), status="published")
    else:
        if current and current.has_perm("project:manage"):
            pass
        else:
            qs = qs.filter(status="published")

    if keyword:
        qs = qs.filter(title__icontains=keyword)
    if tag:
        # JSON 包含由应用层过滤（兼容性更好）
        pass

    if sort == "likes":
        qs = qs.order_by("-like_count", "-id")
    elif sort == "popular":
        # Tortoise 不便表达式排序时先取后排
        qs = qs.order_by("-like_count", "-favorite_count", "-view_count", "-id")
    else:
        qs = qs.order_by("-created_at", "-id")

    projects = await qs.prefetch_related("author")
    if tag:
        projects = [p for p in projects if tag in (p.tags or [])]

    if sort == "popular":
        projects = sorted(projects, key=popularity, reverse=True)

    total = len(projects)
    start = (page - 1) * page_size
    page_items = projects[start : start + page_size]
    items = [await _project_dict(p, current) for p in page_items]
    return ResponseSuccess(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/ranking", summary="人气排行")
async def ranking(
    limit: int = Query(20, ge=1, le=100),
    current: Optional[CurrentUser] = Depends(get_optional_user),
):
    projects = await Project.filter(status="published").prefetch_related("author")
    projects = sorted(projects, key=popularity, reverse=True)[:limit]
    items = []
    for idx, p in enumerate(projects, start=1):
        data = await _project_dict(p, current)
        data["rank"] = idx
        items.append(data)
    return ResponseSuccess(data=items)


@router.get("/{project_id}", summary="作品详情")
async def get_project(
    project_id: int,
    current: Optional[CurrentUser] = Depends(get_optional_user),
):
    project = await Project.get_or_none(id=project_id).prefetch_related("author")
    if not project:
        raise NotFoundException(error_code="PROJECT_NOT_FOUND")
    if project.status != "published":
        if not current or not _can_manage(project, current):
            raise NotFoundException(error_code="PROJECT_NOT_FOUND")
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
    await ProjectLike.filter(project_id=project_id).delete()
    await ProjectFavorite.filter(project_id=project_id).delete()
    await ProjectComment.filter(project_id=project_id).delete()
    await project.delete()
    return ResponseSuccess(data=True)


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

    # 根评论新在前；子回复按时间正序，便于阅读对话
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
    data = _comment_node(comment, reply_to=reply_to)
    return ResponseSuccess(data=data)
