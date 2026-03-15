import os
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Video, User, Category, VideoStatus, VideoSource, VideoVisibility
from app.schemas import VideoResponse, VideoListResponse, MessageResponse
from app.utils.auth import get_current_user
from app.config import settings
import aiofiles

router = APIRouter(prefix="/api/user/videos", tags=["用户-视频管理"])


async def save_upload_file(upload_file: UploadFile, directory: str, filename: Optional[str] = None) -> str:
    """保存上传的文件"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    if filename is None:
        file_extension = upload_file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_extension}"

    file_path = os.path.join(directory, filename)

    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)

    # 计算相对于 UPLOAD_DIR 的路径，确保 URL 包含子目录
    rel_path = os.path.relpath(file_path, settings.UPLOAD_DIR)
    return f"/uploads/{rel_path}"


@router.post("/upload", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    visibility: str = Form("public"),  # public 或 private
    cover_file: Optional[UploadFile] = File(None),
    video_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户上传视频文件"""
    # 验证 visibility 值
    if visibility not in [VideoVisibility.PUBLIC.value, VideoVisibility.PRIVATE.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的权限值，只能是 public 或 private"
        )

    # 验证视频文件扩展名
    file_extension = video_file.filename.split('.')[-1].lower()
    if file_extension not in settings.allowed_video_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型。支持的类型: {', '.join(settings.allowed_video_extensions_list)}"
        )

    # 验证文件大小
    content = await video_file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件过大。最大支持 {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
        )
    await video_file.seek(0)  # 重置文件指针

    # 保存视频文件
    video_url = await save_upload_file(video_file, os.path.join(settings.UPLOAD_DIR, "videos"))

    # 保存封面文件（如果有）
    cover_url = None
    if cover_file:
        cover_extension = cover_file.filename.split('.')[-1].lower()
        if cover_extension not in settings.allowed_image_extensions_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的图片类型。支持的类型: {', '.join(settings.allowed_image_extensions_list)}"
            )
        cover_url = await save_upload_file(cover_file, os.path.join(settings.UPLOAD_DIR, "covers"))

    # 验证分类是否存在
    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )

    # 创建视频记录
    video = Video(
        title=title,
        description=description,
        cover_url=cover_url,
        video_url=video_url,
        video_source=VideoSource.LOCAL,
        category_id=category_id,
        uploader_id=current_user.id,
        visibility=VideoVisibility(visibility),
        status=VideoStatus.PUBLISHED
    )

    db.add(video)
    db.commit()
    db.refresh(video)

    return video


@router.post("/url", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def add_video_by_url(
    title: str = Form(...),
    video_url: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    cover_url: Optional[str] = Form(None),
    visibility: str = Form("public"),  # public 或 private
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户通过URL添加视频"""
    # 验证 visibility 值
    if visibility not in [VideoVisibility.PUBLIC.value, VideoVisibility.PRIVATE.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的权限值，只能是 public 或 private"
        )

    # 验证分类是否存在
    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )

    # 创建视频记录
    video = Video(
        title=title,
        description=description,
        cover_url=cover_url,
        video_url=video_url,
        video_source=VideoSource.URL,
        category_id=category_id,
        uploader_id=current_user.id,
        visibility=VideoVisibility(visibility),
        status=VideoStatus.PUBLISHED
    )

    db.add(video)
    db.commit()
    db.refresh(video)

    return video


@router.get("", response_model=List[VideoListResponse])
async def get_my_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的视频列表（稿件管理）"""
    query = db.query(Video).filter(Video.uploader_id == current_user.id)

    # 状态筛选
    if status:
        query = query.filter(Video.status == status)

    # 搜索标题
    if search:
        query = query.filter(Video.title.contains(search))

    videos = query.order_by(Video.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return videos


@router.get("/{video_id}", response_model=VideoResponse)
async def get_my_video_detail(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的视频详情"""
    video = db.query(Video).filter(Video.id == video_id, Video.uploader_id == current_user.id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在或无权访问"
        )
    return video


@router.put("/{video_id}", response_model=VideoResponse)
async def update_my_video(
    video_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    cover_url: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    visibility: Optional[str] = Form(None),  # public 或 private
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的视频信息"""
    video = db.query(Video).filter(Video.id == video_id, Video.uploader_id == current_user.id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在或无权访问"
        )

    # 更新字段
    if title is not None:
        video.title = title
    if description is not None:
        video.description = description
    if category_id is not None:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        video.category_id = category_id
    if cover_url is not None:
        video.cover_url = cover_url
    if status is not None:
        # 验证状态值
        if status not in [VideoStatus.DRAFT.value, VideoStatus.PUBLISHED.value, VideoStatus.ARCHIVED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的状态值"
            )
        video.status = VideoStatus(status)
    if visibility is not None:
        # 验证 visibility 值
        if visibility not in [VideoVisibility.PUBLIC.value, VideoVisibility.PRIVATE.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的权限值，只能是 public 或 private"
            )
        video.visibility = VideoVisibility(visibility)

    db.commit()
    db.refresh(video)
    return video


@router.delete("/{video_id}", response_model=MessageResponse)
async def delete_my_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除当前用户的视频"""
    video = db.query(Video).filter(Video.id == video_id, Video.uploader_id == current_user.id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在或无权访问"
        )

    # 删除本地文件（如果是本地存储）
    if video.video_source == VideoSource.LOCAL:
        video_path = video.video_url.lstrip('/')
        if os.path.exists(video_path):
            os.remove(video_path)

    db.delete(video)
    db.commit()

    return MessageResponse(message="视频删除成功")
