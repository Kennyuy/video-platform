from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, VideoStatus, VideoSource, VideoVisibility, AudioStatus, AudioSource, AudioVisibility


# 用户相关
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    avatar: Optional[str] = None


class UserResponse(UserBase):
    id: int
    avatar: Optional[str]
    role: str
    coins: int = 0
    created_at: datetime

    @validator('role', pre=True)
    def convert_role(cls, v):
        if isinstance(v, UserRole):
            return v.value
        return v

    class Config:
        orm_mode = True


class UserLoginResponse(BaseModel):
    """登录响应，包含用户信息和硬币奖励"""
    access_token: str
    token_type: str
    user: UserResponse
    daily_login_reward: bool = False  # 是否获得了每日登录奖励
    coins_earned: int = 0  # 获得的硬币数量


# Token 相关
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# 分类相关
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# 视频相关
class VideoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None


class VideoCreate(VideoBase):
    video_url: Optional[str] = None  # 用于URL上传
    cover_url: Optional[str] = None


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    cover_url: Optional[str] = None


class VideoResponse(VideoBase):
    id: int
    cover_url: Optional[str]
    video_url: str
    video_source: str
    uploader_id: int
    uploader: Optional[UserResponse] = None
    category: Optional[CategoryResponse] = None
    duration: int
    views: int
    likes: int
    coins: int
    favorites: int
    shares: int
    visibility: str
    status: str
    created_at: datetime

    @validator('video_source', 'status', 'visibility', pre=True)
    def convert_enum(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        orm_mode = True


class VideoListResponse(BaseModel):
    id: int
    title: str
    cover_url: Optional[str]
    duration: int
    views: int
    likes: int
    favorites: int
    uploader: Optional[UserResponse] = None
    visibility: str
    created_at: datetime

    @validator('visibility', pre=True)
    def convert_visibility(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        orm_mode = True


# 评论相关
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    parent_id: Optional[int] = None


class CommentResponse(CommentBase):
    id: int
    video_id: int
    user: UserResponse
    parent_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True


# 视频互动相关
class VideoInteractionResponse(BaseModel):
    likes: int
    coins: int
    favorites: int
    shares: int
    user_liked: bool
    user_coins: int
    user_favorited: bool

class VideoInteractionAction(BaseModel):
    action: str  # like, coin, favorite, share
    count: Optional[int] = 1  # 用于投币数量

class UserInteractionResponse(BaseModel):
    id: int
    user_id: int
    video_id: int
    liked: int
    coined: int
    favorited: int
    created_at: datetime

    class Config:
        orm_mode = True


# 通用响应
class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int


# 音频相关
class AudioBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None


class AudioCreate(AudioBase):
    audio_url: Optional[str] = None  # 用于URL上传
    cover_url: Optional[str] = None


class AudioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    cover_url: Optional[str] = None


class AudioResponse(AudioBase):
    id: int
    cover_url: Optional[str]
    audio_url: str
    audio_source: str
    uploader_id: int
    uploader: Optional[UserResponse] = None
    category: Optional[CategoryResponse] = None
    duration: int
    plays: int
    likes: int
    coins: int
    favorites: int
    shares: int
    visibility: str
    status: str
    created_at: datetime

    @validator('audio_source', 'status', 'visibility', pre=True)
    def convert_enum(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        orm_mode = True


class AudioListResponse(BaseModel):
    id: int
    title: str
    cover_url: Optional[str]
    duration: int
    plays: int
    likes: int
    favorites: int
    uploader: Optional[UserResponse] = None
    visibility: str
    created_at: datetime

    @validator('visibility', pre=True)
    def convert_visibility(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        orm_mode = True


# 音频互动相关
class AudioInteractionResponse(BaseModel):
    likes: int
    coins: int
    favorites: int
    shares: int
    user_liked: bool
    user_coins: int
    user_favorited: bool


class AudioInteractionAction(BaseModel):
    action: str  # like, coin, favorite, share
    count: Optional[int] = 1  # 用于投币数量
