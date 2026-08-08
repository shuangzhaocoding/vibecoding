# -*- coding: utf-8 -*-
"""华为 OBS 上传封装。"""
import asyncio
import mimetypes
import tempfile
import uuid
from pathlib import Path

from loguru import logger

from app.config.settings import settings
from app.schema import BaseAppException


class HuaweiOBSClient:
    def __init__(self) -> None:
        self._ak = settings.obs_access_key_id
        self._sk = settings.obs_secret_access_key
        self._endpoint = settings.obs_endpoint
        self._bucket = settings.obs_bucket_name
        self._client = None

    def _get_client(self):
        if self._client is None:
            from obs import ObsClient

            self._client = ObsClient(
                access_key_id=self._ak,
                secret_access_key=self._sk,
                server=self._endpoint,
                is_secure=True,
            )
        return self._client

    async def upload_bytes(self, content: bytes, filename: str, prefix: str = "vibecoding/covers/") -> str:
        if not self._ak or not self._sk:
            raise BaseAppException(message="obs not configured", error_code="OBS_INCOMPLETE")

        suffix = Path(filename).suffix or ".bin"
        key = f"{prefix.rstrip('/')}/{uuid.uuid4().hex}{suffix}"
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            client = self._get_client()

            def _upload():
                headers = {"Content-Type": content_type, "x-obs-acl": "public-read"}
                return client.putFile(self._bucket, key, tmp_path, headers=headers)

            resp = await asyncio.to_thread(_upload)
            if resp.status >= 300:
                raise BaseAppException(
                    message="obs upload failed",
                    error_code="OBS_UPLOAD_FAILED",
                    detail={"status": resp.status, "reason": getattr(resp, "reason", "")},
                )
            try:
                await asyncio.to_thread(
                    client.setObjectAcl, self._bucket, key, aclControl="public-read"
                )
            except Exception as acl_exc:
                logger.warning(f"setObjectAcl failed: {acl_exc}")
            return f"https://{self._bucket}.{self._endpoint}/{key}"
        finally:
            Path(tmp_path).unlink(missing_ok=True)


obs_client = HuaweiOBSClient()
