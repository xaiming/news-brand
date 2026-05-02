from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from models.users import User
from typing import List, Optional
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    根据用户名获取用户
    """
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    根据邮箱获取用户
    """
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    根据ID获取用户
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, username: str, email: str, password: str, 
                      nickname: str = None, avatar: str = None, 
                      gender: str = "unknown", bio: str = None, phone: str = None) -> User:
    """
    创建用户
    """
    hashed_password = pwd_context.hash(password)
    
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        nickname=nickname,
        avatar=avatar,
        gender=gender,
        bio=bio,
        phone=phone
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: int, **kwargs) -> Optional[User]:
    """
    更新用户信息
    """
    stmt = update(User).where(User.id == user_id).values(**kwargs)
    await db.execute(stmt)
    await db.commit()
    
    # 获取更新后的用户
    return await get_user(db, user_id)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    用户认证
    """
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user