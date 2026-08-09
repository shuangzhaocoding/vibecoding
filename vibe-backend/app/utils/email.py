# -*- coding: utf-8 -*-
"""邮箱验证码：MySQL 存储 + SMTP 发送。"""
import random
import smtplib
from datetime import datetime, timedelta, timezone
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

from loguru import logger

from app.config.settings import settings
from app.models import EmailCode
from app.schema import BaseAppException

SCENE_COPY = {
    "register": {
        "subject": "VibeCoding 注册验证码",
        "body": "您的 VibeCoding 注册验证码是：{code}\n有效期 {minutes} 分钟，请勿泄露给他人。",
    },
    "reset_password": {
        "subject": "VibeCoding 重置密码验证码",
        "body": "您的 VibeCoding 重置密码验证码是：{code}\n有效期 {minutes} 分钟，请勿泄露给他人。",
    },
}


def _format_addr(s: str) -> str:
    name, addr = parseaddr(s)
    return formataddr((Header(name, "utf-8").encode(), addr))


def _generate_code(length: int = 6) -> str:
    return "".join(random.choice("0123456789") for _ in range(length))


async def can_send_code(email: str, scene: str = "register") -> bool:
    latest = await EmailCode.filter(email=email, scene=scene).order_by("-created_at").first()
    if not latest:
        return True
    created = latest.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - created
    return delta.total_seconds() >= settings.email_code_cooldown_seconds


async def create_and_send_code(email: str, scene: str) -> None:
    email = email.lower()
    if scene not in SCENE_COPY:
        raise BaseAppException(message="invalid scene", error_code="BUSINESS_ERROR")
    if not await can_send_code(email, scene):
        raise BaseAppException(message="send too frequent", error_code="EMAIL_CODE_COOLDOWN")

    if not settings.smtp_username or not settings.smtp_password:
        raise BaseAppException(message="smtp not configured", error_code="SMTP_INCOMPLETE")

    code = _generate_code()
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.email_code_expire_minutes)
    await EmailCode.create(email=email, code=code, scene=scene, expire_at=expire_at)

    copy = SCENE_COPY[scene]
    body = copy["body"].format(code=code, minutes=settings.email_code_expire_minutes)
    message = MIMEText(body, "plain", "utf-8")
    message["From"] = _format_addr(f"{settings.smtp_from_name} <{settings.smtp_username}>")
    message["To"] = _format_addr(f"VibeCoding <{email}>")
    message["Subject"] = Header(copy["subject"], "utf-8")

    try:
        smtp = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.sendmail(settings.smtp_username, [email], message.as_string())
        smtp.quit()
    except Exception as exc:
        logger.exception(exc)
        raise BaseAppException(message="send email failed", error_code="EMAIL_SEND_FAILED") from exc


async def verify_code(email: str, code: str, scene: str) -> bool:
    email = email.lower()
    now = datetime.now(timezone.utc)
    record = (
        await EmailCode.filter(email=email, scene=scene, code=code)
        .order_by("-created_at")
        .first()
    )
    if not record:
        return False
    expire_at = record.expire_at
    if expire_at.tzinfo is None:
        expire_at = expire_at.replace(tzinfo=timezone.utc)
    if expire_at < now:
        return False
    await EmailCode.filter(email=email, scene=scene).delete()
    return True


async def create_and_send_register_code(email: str) -> None:
    await create_and_send_code(email, "register")


async def verify_register_code(email: str, code: str) -> bool:
    return await verify_code(email, code, "register")
