from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# 使用 SQLAlchemy Enum 类型定义枚举值
class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class VideoStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class VideoSource(enum.Enum):
    LOCAL = "local"
    URL = "url"


class VideoVisibility(enum.Enum):
    PUBLIC = "public"      # 所有人可见
    PRIVATE = "private"    # 仅自己可见


class CoinTransactionType(enum.Enum):
    DAILY_LOGIN = "daily_login"      # 每日登录奖励
    COIN_VIDEO = "coin_video"        # 投币给视频
    COIN_AUDIO = "coin_audio"        # 投币给音频
    ADMIN_GRANT = "admin_grant"      # 管理员赠送


class AudioStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AudioSource(enum.Enum):
    LOCAL = "local"
    URL = "url"


class AudioVisibility(enum.Enum):
    PUBLIC = "public"      # 所有人可见
    PRIVATE = "private"   # 仅自己可见


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255))
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.USER)
    coins = Column(Integer, default=0)  # 用户硬币余额
    last_daily_login = Column(Date, nullable=True)  # 最后一次领取每日登录奖励的日期
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    uploaded_videos = relationship("Video", back_populates="uploader")
    uploaded_audios = relationship("Audio", back_populates="uploader")
    comments = relationship("Comment", back_populates="user")
    video_interactions = relationship("UserVideoInteraction", back_populates="user")
    audio_interactions = relationship("UserAudioInteraction", back_populates="user")
    coin_transactions = relationship("CoinTransaction", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    videos = relationship("Video", back_populates="category")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    cover_url = Column(String(500))
    video_url = Column(String(500), nullable=False)
    video_source = Column(Enum(VideoSource, values_callable=lambda x: [e.value for e in x]), default=VideoSource.LOCAL)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    duration = Column(Integer, default=0)  # 视频时长（秒）
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)  # 点赞数
    coins = Column(Integer, default=0)  # 投币数
    favorites = Column(Integer, default=0)  # 收藏数
    shares = Column(Integer, default=0)  # 转发数
    visibility = Column(Enum(VideoVisibility, values_callable=lambda x: [e.value for e in x]), default=VideoVisibility.PUBLIC)  # 浏览权限
    status = Column(Enum(VideoStatus, values_callable=lambda x: [e.value for e in x]), default=VideoStatus.PUBLISHED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index('idx_category', 'category_id'),
        Index('idx_uploader', 'uploader_id'),
        Index('idx_status', 'status'),
        Index('idx_visibility', 'visibility'),
        Index('idx_created_at', 'created_at'),
    )

    # 关系
    category = relationship("Category", back_populates="videos")
    uploader = relationship("User", back_populates="uploaded_videos")
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")
    user_interactions = relationship("UserVideoInteraction", back_populates="video", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 索引
    __table_args__ = (
        Index('idx_video_id', 'video_id'),
        Index('idx_user_id', 'user_id'),
    )

    # 关系
    video = relationship("Video", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id])


class UserVideoInteraction(Base):
    """用户与视频的互动记录（点赞、投币、收藏）"""
    __tablename__ = "user_video_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    liked = Column(Integer, default=0)  # 是否点赞：0=未点赞，1=已点赞
    coined = Column(Integer, default=0)  # 投币数量
    favorited = Column(Integer, default=0)  # 是否收藏：0=未收藏，1=已收藏
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index('idx_uvi_user_id', 'user_id'),
        Index('idx_uvi_video_id', 'video_id'),
        Index('idx_uvi_unique', 'user_id', 'video_id', unique=True),  # 确保每个用户对每个视频只有一条记录
    )

    # 关系
    user = relationship("User", back_populates="video_interactions")
    video = relationship("Video", back_populates="user_interactions")


class CoinTransaction(Base):
    """硬币交易记录"""
    __tablename__ = "coin_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)  # 正数表示获得，负数表示消费
    transaction_type = Column(Enum(CoinTransactionType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="SET NULL"), nullable=True)  # 投币时关联的视频
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 索引
    __table_args__ = (
        Index('idx_ct_user_id', 'user_id'),
        Index('idx_ct_video_id', 'video_id'),
        Index('idx_ct_created_at', 'created_at'),
    )

    # 关系
    user = relationship("User", back_populates="coin_transactions")


class Audio(Base):
    """音频模型"""
    __tablename__ = "audios"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    cover_url = Column(String(500))  # 封面图片
    audio_url = Column(String(500), nullable=False)  # 音频文件URL
    audio_source = Column(Enum(AudioSource, values_callable=lambda x: [e.value for e in x]), default=AudioSource.LOCAL)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    duration = Column(Integer, default=0)  # 音频时长（秒）
    plays = Column(Integer, default=0)  # 播放量
    likes = Column(Integer, default=0)  # 点赞数
    coins = Column(Integer, default=0)  # 投币数
    favorites = Column(Integer, default=0)  # 收藏数
    shares = Column(Integer, default=0)  # 转发数
    visibility = Column(Enum(AudioVisibility, values_callable=lambda x: [e.value for e in x]), default=AudioVisibility.PUBLIC)
    status = Column(Enum(AudioStatus, values_callable=lambda x: [e.value for e in x]), default=AudioStatus.PUBLISHED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index('idx_audio_category', 'category_id'),
        Index('idx_audio_uploader', 'uploader_id'),
        Index('idx_audio_status', 'status'),
        Index('idx_audio_visibility', 'visibility'),
        Index('idx_audio_created_at', 'created_at'),
    )

    # 关系
    category = relationship("Category", foreign_keys=[category_id])
    uploader = relationship("User", back_populates="uploaded_audios")
    user_interactions = relationship("UserAudioInteraction", back_populates="audio", cascade="all, delete-orphan")


class UserAudioInteraction(Base):
    """用户与音频的互动记录（点赞、投币、收藏）"""
    __tablename__ = "user_audio_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    audio_id = Column(Integer, ForeignKey("audios.id", ondelete="CASCADE"), nullable=False)
    liked = Column(Integer, default=0)  # 是否点赞：0=未点赞，1=已点赞
    coined = Column(Integer, default=0)  # 投币数量
    favorited = Column(Integer, default=0)  # 是否收藏：0=未收藏，1=已收藏
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index('idx_uai_user_id', 'user_id'),
        Index('idx_uai_audio_id', 'audio_id'),
        Index('idx_uai_unique', 'user_id', 'audio_id', unique=True),  # 确保每个用户对每个音频只有一条记录
    )

    # 关系
    user = relationship("User", back_populates="audio_interactions")
    audio = relationship("Audio", back_populates="user_interactions")
