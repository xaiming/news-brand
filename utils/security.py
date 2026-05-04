from passlib.context import CryptContext
import hashlib

# 创建密码加密对象加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 密码加密
def get_password_hash(password: str):
    # bcrypt 限制密码长度不能超过 72 字节，先进行 SHA-256 哈希
    if len(password.encode('utf-8')) > 72:
        # 使用 SHA-256 哈希后再用 bcrypt 加密
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return pwd_context.hash(password_hash)
    return pwd_context.hash(password)


# 密码验证
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt 限制密码长度不能超过 72 字节，先进行 SHA-256 哈希
    if len(plain_password.encode('utf-8')) > 72:
        # 使用 SHA-256 哈希后再验证
        plain_password_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        return pwd_context.verify(plain_password_hash, hashed_password)
    return pwd_context.verify(plain_password, hashed_password)
