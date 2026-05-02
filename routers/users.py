from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud.users import create_user, get_user_by_username, get_user, authenticate_user, update_user
from schemas.users import UserCreate, User, UserLogin, Token, TokenData
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 创建路由
router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register")
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    """
    # 检查用户名是否已存在
    db_user = await get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建用户
    new_user = await create_user(
        db,
        username=user.username,
        email=user.email,
        password=user.password,
        nickname=user.nickname,
        avatar=user.avatar,
        gender=user.gender,
        bio=user.bio,
        phone=user.phone
    )
    
    # 生成token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username, "user_id": new_user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "token": access_token,
            "userInfo": {
                "id": new_user.id,
                "username": new_user.username,
                "nickname": new_user.nickname,
                "avatar": new_user.avatar,
                "bio": new_user.bio
            }
        }
    }


@router.post("/login")
async def login_user(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    """
    user = await authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": access_token,
            "userInfo": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "gender": user.gender,
                "bio": user.bio
            }
        }
    }


@router.get("/info")
async def get_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户信息
    """
    return {
        "code": 200,
        "message": "success",
        "data": current_user
    }


@router.put("/update")
async def update_user_info(
    user_update: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户信息
    """
    updated_user = await update_user(db, current_user.id, **user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": updated_user
    }


@router.put("/password")
async def update_user_password(
    oldPassword: str,
    newPassword: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改用户密码
    """
    # 验证旧密码
    if not pwd_context.verify(oldPassword, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    hashed_password = pwd_context.hash(newPassword)
    await update_user(db, current_user.id, hashed_password=hashed_password)
    
    return {
        "code": 200,
        "message": "密码修改成功",
        "data": None
    }


# JWT辅助函数
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user():
    # 这里需要实现JWT验证逻辑
    # 为了简化，这里返回一个模拟的用户对象
    # 在实际项目中，这里应该解析JWT token并验证
    return User(
        id=1,
        username="test_user",
        email="test@example.com",
        nickname=None,
        avatar=None,
        gender="unknown",
        bio=None,
        phone=None,
        is_active=True,
        is_superuser=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )