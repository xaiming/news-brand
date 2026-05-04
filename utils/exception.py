from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from utils.response import fail


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理 FastAPI/Starlette 主动抛出的 HTTPException。"""
    return fail(code=exc.status_code, message=str(exc.detail))


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求参数、请求体等 Pydantic 校验失败。"""
    return fail(code=422, message="参数校验失败", data=exc.errors())


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """处理唯一键、外键等数据库完整性约束异常。"""
    return fail(code=400, message="数据已存在，请勿重复提交")


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理 SQLAlchemy 抛出的通用数据库异常。"""
    return fail(code=500, message="数据库操作失败")


async def global_exception_handler(request: Request, exc: Exception):
    """兜底处理未显式捕获的异常，避免内部错误暴露给前端。"""
    return fail(code=500, message="服务器内部错误")


def register_exception_handlers(app: FastAPI):
    """集中注册异常处理器，最后注册 Exception 作为全局兜底。"""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
