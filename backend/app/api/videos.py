from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Video, Category, VideoVisibility, UserVideoInteraction, User, CoinTransaction, CoinTransactionType
from app.schemas import VideoResponse, VideoListResponse, CategoryResponse, VideoInteractionResponse, VideoInteractionAction
from typing import Optional, List
from app.utils.auth import get_current_user_optional

router = APIRouter(prefix="/api/videos", tags=["视频"])


@router.get("", response_model=List[VideoListResponse])
async def get_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取视频列表（仅返回公开的视频）"""
    query = db.query(Video).filter(
        Video.status == "published",
        Video.visibility == VideoVisibility.PUBLIC
    )

    # 分类筛选
    if category_id:
        query = query.filter(Video.category_id == category_id)

    # 搜索
    if search:
        query = query.filter(Video.title.contains(search))

    total = query.count()
    videos = query.order_by(Video.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return videos


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video_detail(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取视频详情"""
    video = db.query(Video).filter(Video.id == video_id, Video.status == "published").first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )

    # 检查权限：私密视频只有上传者自己能看
    if video.visibility == VideoVisibility.PRIVATE:
        if not current_user or video.uploader_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="视频不存在"
            )

    return video


@router.post("/{video_id}/view")
async def increment_views(video_id: int, db: Session = Depends(get_db)):
    """增加播放量"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )

    video.views += 1
    db.commit()

    return {"views": video.views}


@router.get("/{video_id}/interactions", response_model=VideoInteractionResponse)
async def get_video_interactions(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取视频的互动数据"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )

    # 获取当前用户的互动状态
    user_liked = False
    user_coins = 0
    user_favorited = False

    if current_user:
        interaction = db.query(UserVideoInteraction).filter(
            UserVideoInteraction.user_id == current_user.id,
            UserVideoInteraction.video_id == video_id
        ).first()
        if interaction:
            user_liked = interaction.liked == 1
            user_coins = interaction.coined
            user_favorited = interaction.favorited == 1

    return VideoInteractionResponse(
        likes=video.likes,
        coins=video.coins,
        favorites=video.favorites,
        shares=video.shares,
        user_liked=user_liked,
        user_coins=user_coins,
        user_favorited=user_favorited
    )


@router.post("/{video_id}/interactions")
async def do_interaction(
    video_id: int,
    action_data: VideoInteractionAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """执行互动操作（点赞、投币、收藏、转发）"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录"
        )

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )

    # 获取或创建用户的互动记录
    interaction = db.query(UserVideoInteraction).filter(
        UserVideoInteraction.user_id == current_user.id,
        UserVideoInteraction.video_id == video_id
    ).first()

    if not interaction:
        interaction = UserVideoInteraction(
            user_id=current_user.id,
            video_id=video_id,
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
            video.likes -= 1
            message = "已取消点赞"
        else:
            interaction.liked = 1
            video.likes += 1
            message = "点赞成功"

    elif action == "coin":
        # 投币（每个视频最多投2个）
        if count < 1 or count > 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="每次投币数量必须在1-2之间"
            )
        if interaction.coined + count > 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="每个视频最多投2个币"
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
        video.coins += count

        # 记录硬币交易
        coin_transaction = CoinTransaction(
            user_id=current_user.id,
            amount=-count,  # 负数表示消费
            transaction_type=CoinTransactionType.COIN_VIDEO,
            video_id=video_id,
            description=f"投币给视频《{video.title}》"
        )
        db.add(coin_transaction)
        message = f"投币成功，投了{count}个币"

    elif action == "favorite":
        # 切换收藏状态
        if interaction.favorited == 1:
            interaction.favorited = 0
            video.favorites -= 1
            message = "已取消收藏"
        else:
            interaction.favorited = 1
            video.favorites += 1
            message = "收藏成功"

    elif action == "share":
        # 转发只是增加计数，不需要用户记录
        video.shares += 1
        message = "分享成功"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的操作类型"
        )

    db.commit()
    db.refresh(video)
    db.refresh(interaction)
    db.refresh(current_user)

    return {
        "message": message,
        "likes": video.likes,
        "coins": video.coins,
        "favorites": video.favorites,
        "shares": video.shares,
        "user_liked": interaction.liked == 1,
        "user_coins": interaction.coined,
        "user_favorited": interaction.favorited == 1,
        "user_balance": current_user.coins  # 返回用户当前硬币余额
    }


@router.get("/categories/list", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """获取分类列表"""
    categories = db.query(Category).all()
    return categories
