# -*- coding: utf-8 -*-
"""文件上传（封面、头像等）。"""
from fastapi import APIRouter, Depends, File, UploadFile

from app.common.auth import CurrentUser, PermissionChecking, get_current_user
from app.schema import BaseAppException, ResponseSuccess
from app.utils.obs import obs_client

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024
AVATAR_MAX_SIZE = 2 * 1024 * 1024


async def _read_image(file: UploadFile, max_size: int) -> bytes:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise BaseAppException(message="unsupported file type", error_code="FILE_TYPE_UNSUPPORTED")
    content = await file.read()
    if len(content) > max_size:
        raise BaseAppException(message="file too large", error_code="FILE_TOO_LARGE")
    return content


@router.post("/upload", summary="上传作品封面到 OBS")
async def upload_file(
    file: UploadFile = File(...),
    _: CurrentUser = Depends(PermissionChecking("project:create", "project:update", require_all=False)),
):
    content = await _read_image(file, MAX_SIZE)
    url = await obs_client.upload_bytes(content, file.filename or "cover.jpg", prefix="vibecoding/covers/")
    return ResponseSuccess(data={"url": url})


@router.post("/avatar", summary="上传用户头像到 OBS")
async def upload_avatar(
    file: UploadFile = File(...),
    _: CurrentUser = Depends(get_current_user),
):
    content = await _read_image(file, AVATAR_MAX_SIZE)
    url = await obs_client.upload_bytes(content, file.filename or "avatar.jpg", prefix="vibecoding/avatars/")
    return ResponseSuccess(data={"url": url})
