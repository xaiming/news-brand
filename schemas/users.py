from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class UserInfoBase(BaseModel):
    """用户信息的公共字段，响应和更新请求都可以复用。"""

    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    model_config = ConfigDict(
        from_attributes=True,  # 允许 Pydantic 从 SQLAlchemy ORM 对象中读取属性
    )


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo", description="用户信息")

    model_config = ConfigDict(
        populate_by_name=True,  # 允许用 user_info 字段名给 userInfo 这个别名赋值
        from_attributes=True,
    )


class UserLoginRequest(BaseModel):
    """用户登录请求体。"""

    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class UserUpdateRequest(UserInfoBase):
    """更新用户信息请求体：字段都可选，用户传什么就更新什么。"""

    phone: Optional[str] = Field(None, max_length=11, description="手机号")


class UserPasswordRequest(BaseModel):
    """修改密码请求体，字段名和接口文档保持一致。"""

    old_password: str = Field(..., alias="oldPassword", min_length=6, description="当前密码")
    new_password: str = Field(..., alias="newPassword", min_length=6, description="新密码")

    model_config = ConfigDict(
        populate_by_name=True,  # 既支持 oldPassword，也支持 old_password
    )
