import os
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Audio, User, Category, AudioStatus, AudioSource, AudioVisibility, UserAudioInteraction, CoinTransaction, CoinTransactionType
from app.schemas import AudioResponse, AudioListResponse, CategoryResponse, AudioInteractionResponse, AudioInteractionAction, MessageResponse
from app.utils.auth import get_current_user_optional, get_current_user
from app.config import settings
import aiofiles

router = APIRouter(prefix="/api/audios", tags=["音频"])


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


@router.get("", response_model=List[AudioListResponse])
async def get_audios(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取音频列表（仅返回公开的音频）"""
    query = db.query(Audio).filter(
        Audio.status == "published",
        Audio.visibility == AudioVisibility.PUBLIC
    )

    # 分类筛选
    if category_id:
        query = query.filter(Audio.category_id == category_id)

    # 搜索
    if search:
        query = query.filter(Audio.title.contains(search))

    total = query.count()
    audios = query.order_by(Audio.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return audios


@router.get("/{audio_id}", response_model=AudioResponse)
async def get_audio_detail(
    audio_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取音频详情"""
    audio = db.query(Audio).filter(Audio.id == audio_id, Audio.status == "published").first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频不存在"
        )

    # 检查权限：私密音频只有上传者自己能看
    if audio.visibility == AudioVisibility.PRIVATE:
        if not current_user or audio.uploader_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="音频不存在"
            )

    return audio


@router.post("/{audio_id}/play")
async def increment_plays(audio_id: int, db: Session = Depends(get_db)):
    """增加播放量"""
    audio = db.query(Audio).filter(Audio.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频不存在"
        )

    audio.plays += 1
    db.commit()

    return {"plays": audio.plays}


@router.get("/{audio_id}/interactions", response_model=AudioInteractionResponse)
async def get_audio_interactions(
    audio_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取音频的互动数据"""
    audio = db.query(Audio).filter(Audio.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频不存在"
        )

    # 获取当前用户的互动状态
    user_liked = False
    user_coins = 0
    user_favorited = False

    if current_user:
        interaction = db.query(UserAudioInteraction).filter(
            UserAudioInteraction.user_id == current_user.id,
            UserAudioInteraction.audio_id == audio_id
        ).first()
        if interaction:
            user_liked = interaction.liked == 1
            user_coins = interaction.coined
            user_favorited = interaction.favorited == 1

    return AudioInteractionResponse(
        likes=audio.likes,
        coins=audio.coins,
        favorites=audio.favorites,
        shares=audio.shares,
        user_liked=user_liked,
        user_coins=user_coins,
        user_favorited=user_favorited
    )


@router.post("/{audio_id}/interactions")
async def do_interaction(
    audio_id: int,
    action_data: AudioInteractionAction,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """执行互动操作（点赞、投币、收藏、转发）"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录"
        )

    audio = db.query(Audio).filter(Audio.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频不存在"
        )

    # 获取或创建用户的互动记录
    interaction = db.query(UserAudioInteraction).filter(
        UserAudioInteraction.user_id == current_user.id,
        UserAudioInteraction.audio_id == audio_id
    ).first()

    if not interaction:
        interaction = UserAudioInteraction(
            user_id=current_user.id,
            audio_id=audio_id,
            liked=0,
            coined=0,
            favorited=0
        )
        db.add(interaction)

    action = action_data.action
    count = action_data.count or 1

    if action == "like":
        # 切换点赞状态
        if interaction.liked == 1:
            interaction.liked = 0
            audio.likes -= 1
            message = "已取消点赞"
        else:
            interaction.liked = 1
            audio.likes += 1
            message = "点赞成功"

    elif action == "coin":
        # 投币（每个音频最多投2个）
        if count < 1 or count > 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="每次投币数量必须在1-2之间"
            )
        if interaction.coined + count > 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="每个音频最多投2个币"
            )

        # 检查用户硬币余额
        if current_user.coins < count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="硬币数量不足，投币失败"
            )

        # 扣除用户硬币
        current_user.coins -= count
        interaction.coined += count
        audio.coins += count

        # 记录硬币交易
        coin_transaction = CoinTransaction(
            user_id=current_user.id,
            amount=-count,  # 负数表示消费
            transaction_type=CoinTransactionType.COIN_AUDIO,
            description=f"投币给音频《{audio.title}》"
        )
        db.add(coin_transaction)
        message = f"投币成功，投了{count}个币"

    elif action == "favorite":
        # 切换收藏状态
        if interaction.favorited == 1:
            interaction.favorited = 0
            audio.favorites -= 1
            message = "已取消收藏"
        else:
            interaction.favorited = 1
            audio.favorites += 1
            message = "收藏成功"

    elif action == "share":
        # 转发只是增加计数，不需要用户记录
        audio.shares += 1
        message = "分享成功"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的操作类型"
        )

    db.commit()
    db.refresh(audio)
    db.refresh(interaction)
    db.refresh(current_user)

    return {
        "message": message,
        "likes": audio.likes,
        "coins": audio.coins,
        "favorites": audio.favorites,
        "shares": audio.shares,
        "user_liked": interaction.liked == 1,
        "user_coins": interaction.coined,
        "user_favorited": interaction.favorited == 1,
        "user_balance": current_user.coins
    }


@router.get("/categories/list", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """获取分类列表"""
    categories = db.query(Category).all()
    return categories