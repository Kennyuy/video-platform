import os
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Audio, User, Category, AudioStatus, AudioSource, AudioVisibility
from app.schemas import AudioResponse, AudioListResponse, MessageResponse
from app.utils.auth import get_current_user
from app.config import settings
import aiofiles

router = APIRouter(prefix="/api/user/audios", tags=["用户-音频管理"])


# 支持的音频格式
ALLOWED_AUDIO_EXTENSIONS = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma']


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


@router.post("/upload", response_model=AudioResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    visibility: str = Form("public"),  # public 或 private
    cover_file: Optional[UploadFile] = File(None),
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户上传音频文件"""
    # 验证 visibility 值
    if visibility not in [AudioVisibility.PUBLIC.value, AudioVisibility.PRIVATE.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的权限值，只能是 public 或 private"
        )

    # 验证音频文件扩展名
    file_extension = audio_file.filename.split('.')[-1].lower()
    if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型。支持的类型: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        )

    # 验证文件大小
    content = await audio_file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件过大。最大支持 {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
        )
    await audio_file.seek(0)  # 重置文件指针

    # 保存音频文件
    audio_url = await save_upload_file(audio_file, os.path.join(settings.UPLOAD_DIR, "audios"))

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

    # 创建音频记录
    audio = Audio(
        title=title,
        description=description,
        cover_url=cover_url,
        audio_url=audio_url,
        audio_source=AudioSource.LOCAL,
        category_id=category_id,
        uploader_id=current_user.id,
        visibility=AudioVisibility(visibility),
        status=AudioStatus.PUBLISHED
    )

    db.add(audio)
    db.commit()
    db.refresh(audio)

    return audio


@router.post("/url", response_model=AudioResponse, status_code=status.HTTP_201_CREATED)
async def add_audio_by_url(
    title: str = Form(...),
    audio_url: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    cover_url: Optional[str] = Form(None),
    visibility: str = Form("public"),  # public 或 private
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户通过URL添加音频"""
    # 验证 visibility 值
    if visibility not in [AudioVisibility.PUBLIC.value, AudioVisibility.PRIVATE.value]:
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

    # 创建音频记录
    audio = Audio(
        title=title,
        description=description,
        cover_url=cover_url,
        audio_url=audio_url,
        audio_source=AudioSource.URL,
        category_id=category_id,
        uploader_id=current_user.id,
        visibility=AudioVisibility(visibility),
        status=AudioStatus.PUBLISHED
    )

    db.add(audio)
    db.commit()
    db.refresh(audio)

    return audio


@router.get("", response_model=List[AudioListResponse])
async def get_my_audios(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的音频列表（稿件管理）"""
    query = db.query(Audio).filter(Audio.uploader_id == current_user.id)

    # 状态筛选
    if status:
        query = query.filter(Audio.status == status)

    # 搜索标题
    if search:
        query = query.filter(Audio.title.contains(search))

    audios = query.order_by(Audio.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return audios


@router.get("/{audio_id}", response_model=AudioResponse)
async def get_my_audio_detail(
    audio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的音频详情"""
    audio = db.query(Audio).filter(Audio.id == audio_id, Audio.uploader_id == current_user.id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频不存在或无权访问"
        )
    return audio


@router.put("/{audio_id}", response_model=AudioResponse)
async def update_my_audio(
    audio_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    cover_url: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    visibility: Optional[str] = Form(None),  # public 或 private
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的音频信息"""
    audio = db.query(Audio).filter(Audio.id == audio_id, Audio.uploader_id == current_user.id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频不存在或无权访问"
        )

    # 更新字段
    if title is not None:
        audio.title = title
    if description is not None:
        audio.description = description
    if category_id is not None:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        audio.category_id = category_id
    if cover_url is not None:
        audio.cover_url = cover_url
    if status is not None:
        # 验证状态值
        if status not in [AudioStatus.DRAFT.value, AudioStatus.PUBLISHED.value, AudioStatus.ARCHIVED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的状态值"
            )
        audio.status = AudioStatus(status)
    if visibility is not None:
        # 验证 visibility 值
        if visibility not in [AudioVisibility.PUBLIC.value, AudioVisibility.PRIVATE.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的权限值，只能是 public 或 private"
            )
        audio.visibility = AudioVisibility(visibility)

    db.commit()
    db.refresh(audio)
    return audio


@router.delete("/{audio_id}", response_model=MessageResponse)
async def delete_my_audio(
    audio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除当前用户的音频"""
    audio = db.query(Audio).filter(Audio.id == audio_id, Audio.uploader_id == current_user.id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频不存在或无权访问"
        )

    # 删除本地文件（如果是本地存储）
    if audio.audio_source == AudioSource.LOCAL:
        audio_path = audio.audio_url.lstrip('/')
        if os.path.exists(audio_path):
            os.remove(audio_path)

    db.delete(audio)
    db.commit()

    return MessageResponse(message="音频删除成功")