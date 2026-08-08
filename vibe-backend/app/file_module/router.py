# -*- coding: utf-8 -*-
"""文件上传（封面等）。"""
from fastapi import APIRouter, Depends, File, UploadFile

from app.common.auth import CurrentUser, PermissionChecking
from app.schema import BaseAppException, ResponseSuccess
from app.utils.obs import obs_client

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024


@router.post("/upload", summary="上传文件到 OBS")
async def upload_file(
    file: UploadFile = File(...),
    _: CurrentUser = Depends(PermissionChecking("project:create", "project:update", require_all=False)),
):
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise BaseAppException(message="unsupported file type", error_code="FILE_TYPE_UNSUPPORTED")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise BaseAppException(message="file too large", error_code="FILE_TOO_LARGE")
    url = await obs_client.upload_bytes(content, file.filename or "cover.jpg")
    return ResponseSuccess(data={"url": url})
