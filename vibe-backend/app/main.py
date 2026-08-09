# -*- coding: utf-8 -*-
"""VibeCoding 后端入口。"""
from contextlib import asynccontextmanager
from html import escape

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from loguru import logger
from tortoise import Tortoise

from app.auth_module.router import router as auth_router
from app.config.settings import TORTOISE_ORM, settings
from app.file_module.router import router as file_router
from app.models import Project
from app.project_module.router import router as project_router
from app.schema import BaseAppException, ResponseFailed
from app.seed import seed_data
from app.system_module.router import router as system_router
from app.user_module.router import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("init database...")
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await seed_data()
    logger.info("database ready")
    yield
    await Tortoise.close_connections()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.exception_handler(BaseAppException)
async def app_exception_handler(_: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=200,
        content=ResponseFailed(
            code=exc.code,
            message=exc.message,
            detail={"error_code": exc.error_code, "detail": exc.detail},
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception(exc)
    return JSONResponse(
        status_code=200,
        content=ResponseFailed(
            code=1100,
            message="internal error",
            detail={"error_code": "INTERNAL_ERROR"},
        ).model_dump(),
    )


app.include_router(auth_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(project_router, prefix="/api")
app.include_router(file_router, prefix="/api")
app.include_router(user_router, prefix="/api")


@app.get("/api/health", summary="健康检查")
async def health():
    return {"code": 1200, "message": "ok", "data": True}


def _public_base() -> str:
    return (settings.public_base_url or "").rstrip("/") or "https://vibecoding.yugongcoding.com"


@app.get("/api/sitemap.xml", summary="站点地图")
@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    base = _public_base()
    projects = await Project.filter(status="published").order_by("-updated_at").limit(1000).only("id", "updated_at")
    urls = [
        f"<url><loc>{base}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>",
        f"<url><loc>{base}/ranking</loc><changefreq>daily</changefreq><priority>0.8</priority></url>",
    ]
    for p in projects:
        lastmod = p.updated_at.date().isoformat() if p.updated_at else ""
        loc = f"{base}/projects/{p.id}"
        urls.append(
            f"<url><loc>{loc}</loc>"
            + (f"<lastmod>{lastmod}</lastmod>" if lastmod else "")
            + "<changefreq>weekly</changefreq><priority>0.6</priority></url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(urls)
        + "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


@app.get("/api/og/projects/{project_id}", summary="作品 Open Graph 预览页", response_class=HTMLResponse)
async def project_og(project_id: int):
    """供爬虫读取的 OG HTML；人类浏览器会跳转到前端详情页。"""
    base = _public_base()
    project = await Project.get_or_none(id=project_id, status="published")
    page_url = f"{base}/projects/{project_id}"
    if not project:
        html = f"""<!doctype html><html><head>
<meta charset="utf-8"/><title>Not Found · VibeCoding</title>
<meta http-equiv="refresh" content="0;url={escape(base)}/"/>
</head><body><a href="{escape(base)}/">VibeCoding</a></body></html>"""
        return HTMLResponse(content=html, status_code=404)

    title = escape(project.title or "VibeCoding")
    desc = escape((project.summary or "发现并分享有趣的 AI 作品").strip()[:200])
    image = escape(project.cover_url or f"{base}/favicon-192.png")
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<title>{title} · VibeCoding</title>
<meta name="description" content="{desc}"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="VibeCoding"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="{escape(page_url)}"/>
<meta property="og:image" content="{image}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{title}"/>
<meta name="twitter:description" content="{desc}"/>
<meta name="twitter:image" content="{image}"/>
<link rel="canonical" href="{escape(page_url)}"/>
<meta http-equiv="refresh" content="0;url={escape(page_url)}"/>
</head>
<body>
<p><a href="{escape(page_url)}">{title}</a> — VibeCoding</p>
</body>
</html>"""
    return HTMLResponse(content=html)
