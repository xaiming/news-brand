import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import (
    UserLoginRequest,
    UserPasswordRequest,
    UserRequest,
    UserUpdateRequest,
)
from utils.security import get_password_hash, verify_password


# 根据用户名查询用户是否存在
async def get_user_by_username(username: str, db: AsyncSession):
    query = await db.execute(select(User).where(User.username == username))
    return query.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    # 注册时只保存加密后的密码，不能把明文密码写入数据库。
    hashed_password = get_password_hash(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# 生成 token
async def generate_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)

    # 一个用户只保存一条 token 记录：重复登录时刷新 token 和过期时间。
    query = await db.execute(select(UserToken).where(UserToken.user_id == user_id))
    user_token = query.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)

    await db.commit()
    await db.refresh(user_token)
    return token


# 登录
async def login_user(db: AsyncSession, user_data: UserLoginRequest):
    user = await get_user_by_username(user_data.username, db)
    if not user:
        return None

    # verify_password 的第一个参数是用户输入的明文密码，第二个参数是数据库里的哈希密码。
    if not verify_password(user_data.password, user.password):
        return None

    return user


# 根据 token 获取当前登录用户
async def get_user_by_token(db: AsyncSession, token: str):
    query = await db.execute(select(UserToken).where(UserToken.token == token))
    db_token = query.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None

    user = await db.execute(select(User).where(User.id == db_token.user_id))
    return user.scalar_one_or_none()


# 更新用户信息
async def update_user(db: AsyncSession, user_id: int, update_data: UserUpdateRequest):
    # 先查出当前用户。查不到说明 token 对应的用户不存在，直接返回 None。
    query = await db.execute(select(User).where(User.id == user_id))
    user = query.scalar_one_or_none()
    if not user:
        return None

    # exclude_unset=True 表示只取前端传来的字段。
    # 例如只传 {"bio": "hello"}，就不会把 nickname/avatar 等字段改成 None。
    update_values = update_data.model_dump(exclude_unset=True)

    # 把请求里的字段逐个写回 ORM 对象，SQLAlchemy 会跟踪这些变化。
    for field, value in update_values.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


# 修改用户密码
async def update_user_password(
    db: AsyncSession,
    user: User,
    password_data: UserPasswordRequest,
):
    # 第一步：验证旧密码。只有旧密码正确，才允许设置新密码。
    if not verify_password(password_data.old_password, user.password):
        return False

    # 第二步：把新密码加密后再保存。数据库永远不保存明文密码。
    user.password = get_password_hash(password_data.new_password)

    # 第三步：提交事务并刷新对象，让数据库里的新值生效。
    await db.commit()
    await db.refresh(user)
    return True
