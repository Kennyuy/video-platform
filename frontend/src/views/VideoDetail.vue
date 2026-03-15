<template>
  <el-container class="video-detail-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <el-icon :size="28"><VideoPlay /></el-icon>
          <span>视频平台</span>
        </div>
        <div class="user-actions">
          <template v-if="userStore.isLoggedIn()">
            <div class="coin-balance" v-if="userStore.user">
              <el-icon><Coin /></el-icon>
              <span>{{ userStore.user.coins || 0 }}</span>
            </div>
            <el-dropdown>
              <span class="user-dropdown">
                <el-avatar :size="32" :src="userStore.user?.avatar">
                  {{ userStore.user?.username.charAt(0).toUpperCase() }}
                </el-avatar>
                <span class="username">{{ userStore.user?.username }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/studio')">
                    <el-icon><VideoCamera /></el-icon>
                    创作中心
                  </el-dropdown-item>
                  <el-dropdown-item v-if="userStore.isAdmin()" @click="$router.push('/admin')">
                    <el-icon><Setting /></el-icon>
                    管理后台
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="userStore.logout()">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="$router.push('/login')">登录</el-button>
          </template>
        </div>
      </div>
    </el-header>

    <!-- 主体内容 -->
    <el-main class="main-content" v-loading="loading">
      <template v-if="video">
        <div class="video-container">
          <!-- 视频播放器 -->
          <div class="player-wrapper">
            <div ref="playerRef" class="video-player"></div>
          </div>

          <!-- 视频信息 -->
          <div class="video-info">
            <h1 class="video-title">{{ video.title }}</h1>
            <div class="video-meta">
              <div class="meta-left">
                <el-avatar :size="40" :src="video.uploader?.avatar">
                  {{ video.uploader?.username.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="uploader-info">
                  <div class="uploader-name">{{ video.uploader?.username }}</div>
                  <div class="upload-time">{{ formatDate(video.created_at) }}</div>
                </div>
              </div>
              <div class="meta-right">
                <span class="views">
                  <el-icon><View /></el-icon>
                  {{ formatNumber(video.views) }} 次播放
                </span>
              </div>
            </div>

            <!-- 互动按钮区域 -->
            <div class="interaction-bar">
              <div class="interaction-item">
                <el-button
                  :type="interactions.user_liked ? 'primary' : 'default'"
                  :loading="interactionLoading === 'like'"
                  @click="handleLike"
                >
                  <el-icon><Pointer /></el-icon>
                  <span class="count">{{ formatNumber(interactions.likes) }}</span>
                </el-button>
                <span class="label">点赞</span>
              </div>

              <div class="interaction-item">
                <el-dropdown @command="handleCoin" :disabled="interactionLoading === 'coin'">
                  <el-button :type="interactions.user_coins > 0 ? 'warning' : 'default'">
                    <el-icon><Coin /></el-icon>
                    <span class="count">{{ formatNumber(interactions.coins) }}</span>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="1">投 1 币</el-dropdown-item>
                      <el-dropdown-item command="2">投 2 币</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <span class="label">投币{{ interactions.user_coins > 0 ? `(${interactions.user_coins})` : '' }}</span>
              </div>

              <div class="interaction-item">
                <el-button
                  :type="interactions.user_favorited ? 'danger' : 'default'"
                  :loading="interactionLoading === 'favorite'"
                  @click="handleFavorite"
                >
                  <el-icon><Star /></el-icon>
                  <span class="count">{{ formatNumber(interactions.favorites) }}</span>
                </el-button>
                <span class="label">收藏</span>
              </div>

              <div class="interaction-item">
                <el-button
                  :loading="interactionLoading === 'share'"
                  @click="handleShare"
                >
                  <el-icon><Share /></el-icon>
                  <span class="count">{{ formatNumber(interactions.shares) }}</span>
                </el-button>
                <span class="label">转发</span>
              </div>
            </div>

            <!-- 视频简介 -->
            <div v-if="video.description" class="video-description">
              <div class="description-title">简介</div>
              <div class="description-content">{{ video.description }}</div>
            </div>
          </div>
        </div>

        <!-- 评论区域 -->
        <div class="comments-section">
          <div class="comments-title">评论 (0)</div>
          <!-- 评论输入框 -->
          <div class="comment-input">
            <el-input
              v-model="commentText"
              type="textarea"
              :rows="3"
              placeholder="发表你的看法..."
            />
            <div class="comment-actions">
              <el-button
                type="primary"
                :disabled="!commentText.trim() || !userStore.isLoggedIn()"
                @click="submitComment"
              >
                发表评论
              </el-button>
            </div>
          </div>
        </div>
      </template>
      <el-empty v-else description="视频不存在" />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import DPlayer from 'dplayer'
import { VideoPlay, View, Pointer, Coin, Star, Share, VideoCamera, Setting, SwitchButton } from '@element-plus/icons-vue'
import { videoApi } from '@/api'
import { useUserStore } from '@/store/user'
import type { Video, VideoInteraction } from '@/types'
import { ElMessage } from 'element-plus'

// API 基础 URL - 使用当前页面 origin
const API_BASE_URL = ''  // 空字符串表示使用相对路径，同源部署

const route = useRoute()
const userStore = useUserStore()

const video = ref<Video | null>(null)
const loading = ref(false)
const playerRef = ref<HTMLElement>()
const player = ref<DPlayer>()
const commentText = ref('')
const interactions = ref<VideoInteraction>({
  likes: 0,
  coins: 0,
  favorites: 0,
  shares: 0,
  user_liked: false,
  user_coins: 0,
  user_favorited: false
})
const interactionLoading = ref<string | null>(null)

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`

  return date.toLocaleDateString('zh-CN')
}

// 获取完整的视频 URL
const getVideoUrl = (url: string) => {
  if (url.startsWith('http')) {
    return url
  }
  // 相对路径，拼接 API 基础 URL
  return `${API_BASE_URL}${url}`
}

// 初始化播放器
const initPlayer = () => {
  if (!playerRef.value || !video.value) return

  player.value = new DPlayer({
    container: playerRef.value,
    video: {
      url: getVideoUrl(video.value.video_url),
      type: 'auto'
    },
    theme: '#409EFF',
    autoplay: false,
    loop: false,
    lang: 'zh-cn',
    screenshot: true,
    hotkey: true,
    preload: 'auto',
    volume: 0.7,
    mutex: true,
  })

  // 增加播放量
  videoApi.incrementViews(video.value.id)
}

// 提交评论
const submitComment = () => {
  if (!commentText.value.trim()) return
  ElMessage.success('评论功能开发中')
  commentText.value = ''
}

// 加载视频详情
const loadVideoDetail = async () => {
  loading.value = true
  try {
    const videoId = Number(route.params.id)
    video.value = await videoApi.getVideoDetail(videoId)

    // 视频加载完成后初始化播放器
    setTimeout(() => {
      initPlayer()
    }, 100)

    // 加载互动数据
    await loadInteractions()
  } catch (error) {
    console.error('加载视频失败', error)
  } finally {
    loading.value = false
  }
}

// 加载互动数据
const loadInteractions = async () => {
  if (!video.value) return
  try {
    interactions.value = await videoApi.getInteractions(video.value.id)
  } catch (error) {
    console.error('加载互动数据失败', error)
  }
}

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

// 点赞
const handleLike = async () => {
  if (!userStore.isLoggedIn()) {
    ElMessage.warning('请先登录')
    return
  }
  if (!video.value || interactionLoading.value) return

  interactionLoading.value = 'like'
  try {
    const result = await videoApi.doInteraction(video.value.id, 'like')
    interactions.value = {
      likes: result.likes,
      coins: result.coins,
      favorites: result.favorites,
      shares: result.shares,
      user_liked: result.user_liked,
      user_coins: result.user_coins,
      user_favorited: result.user_favorited
    }
    ElMessage.success(result.message)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    interactionLoading.value = null
  }
}

// 投币
const handleCoin = async (count: number) => {
  if (!userStore.isLoggedIn()) {
    ElMessage.warning('请先登录')
    return
  }
  if (!video.value || interactionLoading.value) return

  interactionLoading.value = 'coin'
  try {
    const result = await videoApi.doInteraction(video.value.id, 'coin', count)
    interactions.value = {
      likes: result.likes,
      coins: result.coins,
      favorites: result.favorites,
      shares: result.shares,
      user_liked: result.user_liked,
      user_coins: result.user_coins,
      user_favorited: result.user_favorited
    }
    // 更新用户硬币余额
    if (result.user_balance !== undefined) {
      userStore.updateCoins(result.user_balance)
    }
    ElMessage.success(result.message)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    interactionLoading.value = null
  }
}

// 收藏
const handleFavorite = async () => {
  if (!userStore.isLoggedIn()) {
    ElMessage.warning('请先登录')
    return
  }
  if (!video.value || interactionLoading.value) return

  interactionLoading.value = 'favorite'
  try {
    const result = await videoApi.doInteraction(video.value.id, 'favorite')
    interactions.value = {
      likes: result.likes,
      coins: result.coins,
      favorites: result.favorites,
      shares: result.shares,
      user_liked: result.user_liked,
      user_coins: result.user_coins,
      user_favorited: result.user_favorited
    }
    ElMessage.success(result.message)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    interactionLoading.value = null
  }
}

// 转发
const handleShare = async () => {
  if (!video.value || interactionLoading.value) return

  interactionLoading.value = 'share'
  try {
    const result = await videoApi.doInteraction(video.value.id, 'share')
    interactions.value = {
      likes: result.likes,
      coins: result.coins,
      favorites: result.favorites,
      shares: result.shares,
      user_liked: result.user_liked,
      user_coins: result.user_coins,
      user_favorited: result.user_favorited
    }

    // 复制链接到剪贴板
    const url = window.location.href
    try {
      await navigator.clipboard.writeText(url)
      ElMessage.success('链接已复制到剪贴板')
    } catch {
      ElMessage.success('分享成功')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    interactionLoading.value = null
  }
}

onMounted(() => {
  loadVideoDetail()
})

onUnmounted(() => {
  if (player.value) {
    player.value.destroy()
  }
})
</script>

<style scoped lang="scss">
.video-detail-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;

  .header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    padding: 0 16px;

    @media (max-width: 768px) {
      padding: 0 12px;
    }
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 20px;
    font-weight: 600;
    color: var(--el-color-primary);
    cursor: pointer;
    user-select: none;
    white-space: nowrap;

    @media (max-width: 768px) {
      font-size: 16px;
      gap: 4px;

      span {
        display: none;
      }
    }
  }

  .user-actions {
    display: flex;
    gap: 12px;
    align-items: center;

    @media (max-width: 768px) {
      gap: 8px;
    }

    .coin-balance {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 12px;
      background: linear-gradient(135deg, #ffd700, #ffb347);
      border-radius: 16px;
      color: #fff;
      font-weight: 500;
      font-size: 14px;

      @media (max-width: 768px) {
        padding: 4px 8px;
        font-size: 12px;

        span {
          display: none;
        }
      }

      .el-icon {
        font-size: 16px;
      }
    }

    .user-dropdown {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;

      @media (max-width: 768px) {
        gap: 4px;

        .username {
          display: none;
        }
      }
    }
  }
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 16px;

  @media (max-width: 768px) {
    padding: 16px 12px;
  }
}

.video-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;

  @media (max-width: 768px) {
    gap: 16px;
  }
}

.player-wrapper {
  background: #000;
  border-radius: 12px;
  overflow: hidden;

  @media (max-width: 768px) {
    border-radius: 8px;
  }
}

.video-player {
  width: 100%;
  aspect-ratio: 16/9;
}

.video-info {
  background: #fff;
  padding: 20px;
  border-radius: 12px;

  @media (max-width: 768px) {
    padding: 16px;
    border-radius: 8px;
  }
}

.video-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #333;

  @media (max-width: 768px) {
    font-size: 16px;
    margin-bottom: 12px;
  }
}

.video-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
  margin-bottom: 16px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding-bottom: 12px;
    margin-bottom: 12px;
  }
}

.meta-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.uploader-info {
  .uploader-name {
    font-weight: 500;
    color: #333;

    @media (max-width: 768px) {
      font-size: 14px;
    }
  }

  .upload-time {
    font-size: 12px;
    color: #999;
  }
}

.meta-right {
  .views {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #666;

    @media (max-width: 768px) {
      font-size: 13px;
    }
  }
}

.video-description {
  margin-top: 16px;
}

.description-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;

  @media (max-width: 768px) {
    font-size: 14px;
  }
}

.description-content {
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;

  @media (max-width: 768px) {
    font-size: 13px;
  }
}

.interaction-bar {
  display: flex;
  gap: 24px;
  padding: 16px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 16px;

  @media (max-width: 768px) {
    gap: 12px;
    padding: 12px 0;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;

    &::-webkit-scrollbar {
      display: none;
    }
  }
}

.interaction-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;

  .el-button {
    min-width: 80px;

    @media (max-width: 768px) {
      min-width: 60px;
      padding: 8px 12px;
    }
  }

  .count {
    margin-left: 4px;

    @media (max-width: 768px) {
      font-size: 12px;
    }
  }

  .label {
    font-size: 12px;
    color: #999;

    @media (max-width: 768px) {
      font-size: 10px;
    }
  }
}

.comments-section {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  margin-top: 24px;

  @media (max-width: 768px) {
    padding: 16px;
    border-radius: 8px;
    margin-top: 16px;
  }
}

.comments-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;

  @media (max-width: 768px) {
    font-size: 15px;
    margin-bottom: 12px;
  }
}

.comment-input {
  margin-bottom: 24px;
}

.comment-actions {
  margin-top: 12px;
  text-align: right;
}

@media (min-width: 1200px) {
  .video-container {
    grid-template-columns: 1fr 400px;
  }

  .player-wrapper {
    grid-column: 1 / -1;
  }

  .video-info {
    grid-column: 1;
  }

  .comments-section {
    grid-column: 2;
  }
}
</style>
