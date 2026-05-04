from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def response(code: int, message: str, data=None, http_status: int = 200):
    """统一响应出口，业务状态通过 JSON 的 code 字段表达。"""
    content = {"code": code, "message": message, "data": data}
    return JSONResponse(
        status_code=http_status,
        # jsonable_encoder 可以处理 Pydantic、ORM、datetime 等对象。
        content=jsonable_encoder(content),
    )


def success(data=None, message: str = "success", code: int = 200):
    """成功响应的快捷方法。"""
    return response(code=code, message=message, data=data)


def fail(message: str = "error", code: int = 400, data=None):
    """失败响应的快捷方法，默认仍返回 HTTP 200。"""
    return response(code=code, message=message, data=data)
