from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.users import (
    create_user,
    generate_token,
    get_user_by_username,
    login_user,
    update_user,
    update_user_password,
)
from models.users import User
from schemas.users import (
    UserAuthResponse,
    UserInfoResponse,
    UserLoginRequest,
    UserPasswordRequest,
    UserRequest,
    UserUpdateRequest,
)
from utils.auth import get_current_user
from utils.response import success

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    user_in_db = await get_user_by_username(user_data.username, db)
    if user_in_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = await create_user(db, user_data)
    token = await generate_token(db, user.id)

    response_data = UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user),
    )

    return success(data=response_data, message="注册成功")


# 登录接口
@router.post("/login")
async def login(user_data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    # 登录成功后生成 token，并把 token 和用户信息一起返回给前端保存。
    user = await login_user(db, user_data)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在或密码错误")

    token = await generate_token(db, user.id)
    response_data = UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user),
    )

    return success(message="登录成功", data=response_data)


# 获取登录用户信息
@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success(
        message="获取用户信息成功",
        data=UserInfoResponse.model_validate(user),
    )


# 更新用户信息
@router.put("/update")
async def update_user_info(
    update_data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # current_user 来自 get_current_user，它会根据 Authorization 请求头查出当前登录用户。
    updated_user = await update_user(db, current_user.id, update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 返回更新后的用户信息，前端可以直接用它刷新页面上的个人资料。
    return success(
        message="更新用户信息成功",
        data=UserInfoResponse.model_validate(updated_user),
    )


# 修改用户密码
@router.put("/password")
async def change_user_password(
    password_data: UserPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 这个接口也需要登录，所以同样通过 Depends(get_current_user) 验证 token。
    password_changed = await update_user_password(db, current_user, password_data)
    if not password_changed:
        raise HTTPException(status_code=400, detail="当前密码错误")

    return success(message="密码修改成功", data=None)
