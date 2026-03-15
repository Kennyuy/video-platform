from app.api.auth import router as auth_router
from app.api.admin_videos import router as admin_videos_router
from app.api.videos import router as videos_router
from app.api.user_videos import router as user_videos_router
from app.api.audios import router as audios_router
from app.api.user_audios import router as user_audios_router

# 导出路由
auth = auth_router
admin_videos = admin_videos_router
videos = videos_router
user_videos = user_videos_router
audios = audios_router
user_audios = user_audios_router
