<template>
  <el-container class="audio-detail-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <el-icon :size="28"><Headset /></el-icon>
          <span>音频平台</span>
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
      <template v-if="audio">
        <div class="audio-container">
          <!-- 音频封面 -->
          <div class="cover-wrapper">
            <div class="audio-cover">
              <img v-if="audio.cover_url" :src="getFullUrl(audio.cover_url)" :alt="audio.title" />
              <div v-else class="no-cover">
                <el-icon :size="80"><Headset /></el-icon>
              </div>
            </div>
          </div>

          <!-- 音频播放器 -->
          <div class="player-wrapper">
            <audio ref="audioRef" class="audio-player" controls @play="onPlay">
              <source :src="getFullUrl(audio.audio_url)" type="audio/mpeg">
              您的浏览器不支持音频播放
            </audio>
          </div>

          <!-- 音频信息 -->
          <div class="audio-info">
            <h1 class="audio-title">{{ audio.title }}</h1>
            <div class="audio-meta">
              <div class="meta-left">
                <el-avatar :size="40" :src="audio.uploader?.avatar">
                  {{ audio.uploader?.username.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="uploader-info">
                  <div class="uploader-name">{{ audio.uploader?.username }}</div>
                  <div class="upload-time">{{ formatDate(audio.created_at) }}</div>
                </div>
              </div>
              <div class="meta-right">
                <span class="plays">
                  <el-icon><Headset /></el-icon>
                  {{ formatNumber(audio.plays) }} 次播放
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

            <!-- 音频简介 -->
            <div v-if="audio.description" class="audio-description">
              <div class="description-title">简介</div>
              <div class="description-content">{{ audio.description }}</div>
            </div>
          </div>
        </div>
      </template>
      <el-empty v-else description="音频不存在" />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { Headset, Coin, Pointer, Star, Share, VideoCamera, Setting, SwitchButton } from '@element-plus/icons-vue'
import { audioApi } from '@/api'
import { useUserStore } from '@/store/user'
import type { Audio, AudioInteraction } from '@/types'
import { ElMessage } from 'element-plus'

const route = useRoute()
const userStore = useUserStore()

const audio = ref<Audio | null>(null)
const loading = ref(false)
const audioRef = ref<HTMLAudioElement>()
const interactions = ref<AudioInteraction>({
  likes: 0,
  coins: 0,
  favorites: 0,
  shares: 0,
  user_liked: false,
  user_coins: 0,
  user_favorited: false
})
const interactionLoading = ref<string | null>(null)
const hasPlayed = ref(false)

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

// 获取完整的资源 URL
const getFullUrl = (url: string | undefined) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return url
}

// 加载音频详情
const loadAudioDetail = async () => {
  loading.value = true
  try {
    const audioId = Number(route.params.id)
    audio.value = await audioApi.getAudioDetail(audioId)

    // 加载互动数据
    await loadInteractions()
  } catch (error) {
    console.error('加载音频失败', error)
  } finally {
    loading.value = false
  }
}

// 加载互动数据
const loadInteractions = async () => {
  if (!audio.value) return
  try {
    interactions.value = await audioApi.getInteractions(audio.value.id)
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

// 播放时增加播放量
const onPlay = () => {
  if (!hasPlayed.value && audio.value) {
    hasPlayed.value = true
    audioApi.incrementPlays(audio.value.id)
  }
}

// 点赞
const handleLike = async () => {
  if (!userStore.isLoggedIn()) {
    ElMessage.warning('请先登录')
    return
  }
  if (!audio.value || interactionLoading.value) return

  interactionLoading.value = 'like'
  try {
    const result = await audioApi.doInteraction(audio.value.id, 'like')
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
  if (!audio.value || interactionLoading.value) return

  interactionLoading.value = 'coin'
  try {
    const result = await audioApi.doInteraction(audio.value.id, 'coin', count)
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
  if (!audio.value || interactionLoading.value) return

  interactionLoading.value = 'favorite'
  try {
    const result = await audioApi.doInteraction(audio.value.id, 'favorite')
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
  if (!audio.value || interactionLoading.value) return

  interactionLoading.value = 'share'
  try {
    const result = await audioApi.doInteraction(audio.value.id, 'share')
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
  loadAudioDetail()
})

onUnmounted(() => {
  if (audioRef.value) {
    audioRef.value.pause()
  }
})
</script>

<style scoped lang="scss">
.audio-detail-container {
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px 16px;

  @media (max-width: 768px) {
    padding: 16px 12px;
  }
}

.audio-container {
  display: flex;
  flex-direction: column;
  gap: 24px;

  @media (max-width: 768px) {
    gap: 16px;
  }
}

.cover-wrapper {
  display: flex;
  justify-content: center;
}

.audio-cover {
  width: 300px;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;

  @media (max-width: 768px) {
    width: 200px;
    height: 200px;
    border-radius: 8px;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .no-cover {
    color: rgba(255, 255, 255, 0.8);

    @media (max-width: 768px) {
      .el-icon {
        font-size: 60px !important;
      }
    }
  }
}

.player-wrapper {
  background: #f5f5f5;
  border-radius: 12px;
  padding: 20px;

  @media (max-width: 768px) {
    padding: 16px;
    border-radius: 8px;
  }
}

.audio-player {
  width: 100%;
  height: 50px;

  @media (max-width: 768px) {
    height: 40px;
  }
}

.audio-info {
  background: #fff;
  padding: 20px;
  border-radius: 12px;

  @media (max-width: 768px) {
    padding: 16px;
    border-radius: 8px;
  }
}

.audio-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #333;

  @media (max-width: 768px) {
    font-size: 18px;
    margin-bottom: 12px;
  }
}

.audio-meta {
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
  .plays {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #666;

    @media (max-width: 768px) {
      font-size: 13px;
    }
  }
}

.audio-description {
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
</style>