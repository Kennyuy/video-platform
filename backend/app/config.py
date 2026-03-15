from pydantic import BaseSettings
from typing import List
import os


# 先尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    # 获取当前文件所在目录的 .env 文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, "..", ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        # 尝试加载当前工作目录的 .env
        load_dotenv()
except ImportError:
    pass


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # JWT 配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # 应用配置
    APP_NAME: str = "Video Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 524288000  # 500MB
    ALLOWED_VIDEO_EXTENSIONS: str = "mp4,mkv,avi,mov"
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,gif"

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_video_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_VIDEO_EXTENSIONS.split(",")]

    @property
    def allowed_image_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(",")]

    class Config:
        # 允许从环境变量读取
        env_file_encoding = "utf-8"


settings = Settings()
