# 根据token查询用户信息 返回用户信息
from fastapi import Header, HTTPException

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.users import get_user_by_token


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    token = authorization.replace("Bearer ", "")
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的token")
    return user
