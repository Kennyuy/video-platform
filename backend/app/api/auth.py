from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import User, CoinTransaction, CoinTransactionType
from app.schemas import UserCreate, UserResponse, UserUpdate, Token, UserLoginResponse
from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/api/auth", tags=["认证"])

# 每日登录奖励硬币数量
DAILY_LOGIN_COINS = 2


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否存在
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否存在
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 创建新用户
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        coins=0  # 新用户初始硬币为0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=UserLoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查是否可以获得每日登录奖励
    daily_login_reward = False
    coins_earned = 0
    today = date.today()

    if user.last_daily_login is None or user.last_daily_login < today:
        # 发放每日登录奖励
        user.coins += DAILY_LOGIN_COINS
        user.last_daily_login = today

        # 记录硬币交易
        transaction = CoinTransaction(
            user_id=user.id,
            amount=DAILY_LOGIN_COINS,
            transaction_type=CoinTransactionType.DAILY_LOGIN,
            description="每日登录奖励"
        )
        db.add(transaction)
        db.commit()
        db.refresh(user)

        daily_login_reward = True
        coins_earned = DAILY_LOGIN_COINS

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.username})

    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
        daily_login_reward=daily_login_reward,
        coins_earned=coins_earned
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    if user_update.avatar is not None:
        current_user.avatar = user_update.avatar

    db.commit()
    db.refresh(current_user)
    return current_user
