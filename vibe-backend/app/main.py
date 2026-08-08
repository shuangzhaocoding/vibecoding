# -*- coding: utf-8 -*-
"""VibeCoding 后端入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from tortoise import Tortoise

from app.auth_module.router import router as auth_router
from app.config.settings import TORTOISE_ORM, settings
from app.file_module.router import router as file_router
from app.project_module.router import router as project_router
from app.schema import BaseAppException, ResponseFailed
from app.seed import seed_data
from app.system_module.router import router as system_router


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


@app.get("/api/health", summary="健康检查")
async def health():
    return {"code": 1200, "message": "ok", "data": True}
