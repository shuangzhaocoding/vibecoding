# -*- coding: utf-8 -*-
"""从 Request 提取客户端信息。"""
from fastapi import Request


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64] or "unknown"
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()[:64]
    if request.client and request.client.host:
        return request.client.host
    return "unknown"
