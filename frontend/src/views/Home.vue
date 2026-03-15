<template>
  <el-container class="home-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <el-icon :size="28"><VideoPlay /></el-icon>
          <span>媒体平台</span>
        </div>
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索视频"
            :prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>
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
            <el-button @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </el-header>

    <!-- 主体内容 -->
    <el-main class="main-content">
      <!-- 分类筛选 -->
      <div class="category-filter">
        <el-button
          v-for="category in categories"
          :key="category.id"
          :type="selectedCategory === category.id ? 'primary' : 'default'"
          size="small"
          @click="selectedCategory = category.id; loadVideos(); loadAudios()"
        >
          {{ category.name }}
        </el-button>
        <el-button
          :type="selectedCategory === null ? 'primary' : 'default'"
          size="small"
          @click="selectedCategory = null; loadVideos(); loadAudios()"
        >
          全部
        </el-button>
      </div>

      <!-- 视频区域 -->
      <div class="section">
        <div class="section-header">
          <h2><el-icon><VideoPlay /></el-icon> 视频</h2>
          <el-button text @click="$router.push('/videos')">查看更多</el-button>
        </div>
        <div v-loading="videoLoading" class="video-grid">
          <div
            v-for="video in videos"
            :key="video.id"
            class="video-card"
            @click="$router.push(`/video/${video.id}`)"
          >
            <div class="video-cover">
              <img v-if="video.cover_url" :src="getFullUrl(video.cover_url)" :alt="video.title" />
              <div v-else class="no-cover">
                <el-icon :size="40"><VideoPlay /></el-icon>
              </div>
              <div class="video-duration">{{ formatDuration(video.duration) }}</div>
            </div>
            <div class="video-info">
              <div class="video-title" :title="video.title">{{ video.title }}</div>
              <div class="video-meta">
                <span>{{ video.uploader?.username || '未知' }}</span>
                <span>{{ video.views }} 次播放</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 音频区域 -->
      <div class="section">
        <div class="section-header">
          <h2><el-icon><Headset /></el-icon> 音频</h2>
          <el-button text @click="$router.push('/audios')">查看更多</el-button>
        </div>
        <div v-loading="audioLoading" class="audio-grid">
          <div
            v-for="audio in audios"
            :key="audio.id"
            class="audio-card"
            @click="$router.push(`/audio/${audio.id}`)"
          >
            <div class="audio-cover">
              <img v-if="audio.cover_url" :src="getFullUrl(audio.cover_url)" :alt="audio.title" />
              <div v-else class="no-cover">
                <el-icon :size="40"><Headset /></el-icon>
              </div>
            </div>
            <div class="audio-info">
              <div class="audio-title" :title="audio.title">{{ audio.title }}</div>
              <div class="audio-meta">
                <span>{{ audio.uploader?.username || '未知' }}</span>
                <span>{{ audio.plays }} 次播放</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 视频分页 -->
      <div class="pagination" v-if="videos.length > 0">
        <el-pagination
          v-model:current-page="videoPage"
          v-model:page-size="videoPageSize"
          :total="videoTotal"
          :page-sizes="[6, 12, 24]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadVideos"
          @size-change="loadVideos"
        />
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { VideoPlay, Search, VideoCamera, Setting, SwitchButton, Coin, Headset } from '@element-plus/icons-vue'
import { videoApi, categoryApi, audioApi } from '@/api'
import { useUserStore } from '@/store/user'
import type { Video, Category, Audio } from '@/types'

const userStore = useUserStore()

// 获取完整的资源 URL
const getFullUrl = (url: string | undefined) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return url
}

const videos = ref<Video[]>([])
const audios = ref<Audio[]>([])
const categories = ref<Category[]>([])
const videoLoading = ref(false)
const audioLoading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref<number | null>(null)
const videoPage = ref(1)
const videoPageSize = ref(6)
const videoTotal = ref(0)
const audioPage = ref(1)
const audioPageSize = ref(6)
const audioTotal = ref(0)

// 格式化时长
const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// 加载分类
const loadCategories = async () => {
  try {
    categories.value = await categoryApi.getCategories()
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

// 加载视频
const loadVideos = async () => {
  videoLoading.value = true
  try {
    const params: any = {
      page: videoPage.value,
      page_size: videoPageSize.value
    }
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const data = await videoApi.getVideos(params)
    videos.value = data.data || data
    videoTotal.value = videos.value.length
  } catch (error) {
    console.error('加载视频失败', error)
  } finally {
    videoLoading.value = false
  }
}

// 加载音频
const loadAudios = async () => {
  audioLoading.value = true
  try {
    const params: any = {
      page: audioPage.value,
      page_size: audioPageSize.value
    }
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const data = await audioApi.getAudios(params)
    audios.value = data || []
    audioTotal.value = audios.value.length
  } catch (error) {
    console.error('加载音频失败', error)
  } finally {
    audioLoading.value = false
  }
}

// 搜索
const handleSearch = () => {
  videoPage.value = 1
  audioPage.value = 1
  loadVideos()
  loadAudios()
}

onMounted(() => {
  loadCategories()
  loadVideos()
  loadAudios()
})
</script>

<style scoped lang="scss">
.home-container {
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
    height: 64px;
    gap: 24px;
    padding: 0 16px;

    @media (max-width: 768px) {
      gap: 12px;
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

  .search-box {
    flex: 1;
    max-width: 500px;

    @media (max-width: 768px) {
      max-width: none;
    }

    :deep(.el-input-group__append) {
      background: var(--el-color-primary);
      color: #fff;
      border-color: var(--el-color-primary);

      .el-button {
        color: #fff;
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

.category-filter {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    gap: 8px;
    margin-bottom: 16px;
  }
}

.section {
  margin-bottom: 40px;

  @media (max-width: 768px) {
    margin-bottom: 24px;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  @media (max-width: 768px) {
    margin-bottom: 12px;
  }

  h2 {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 20px;
    font-weight: 600;
    color: #333;
    margin: 0;

    @media (max-width: 768px) {
      font-size: 16px;
      gap: 4px;
    }
  }
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;

  @media (min-width: 1200px) {
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
  }

  @media (min-width: 900px) and (max-width: 1199px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  @media (min-width: 600px) and (max-width: 899px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  @media (max-width: 599px) {
    grid-template-columns: repeat(1, 1fr);
    gap: 12px;
  }
}

.video-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;

  @media (min-width: 769px) {
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }
  }

  @media (max-width: 768px) {
    border-radius: 6px;
  }
}

.video-cover {
  position: relative;
  aspect-ratio: 16/9;
  background: #f0f0f0;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .no-cover {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ccc;
  }

  .video-duration {
    position: absolute;
    bottom: 8px;
    right: 8px;
    background: rgba(0, 0, 0, 0.7);
    color: #fff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;

    @media (max-width: 768px) {
      bottom: 4px;
      right: 4px;
      font-size: 11px;
      padding: 2px 4px;
    }
  }
}

.video-info {
  padding: 12px;

  @media (max-width: 768px) {
    padding: 10px;
  }
}

.video-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #333;

  @media (max-width: 768px) {
    font-size: 13px;
    margin-bottom: 6px;
  }
}

.video-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;

  @media (max-width: 768px) {
    font-size: 11px;
  }
}

.audio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;

  @media (min-width: 1200px) {
    grid-template-columns: repeat(6, 1fr);
    gap: 24px;
  }

  @media (min-width: 900px) and (max-width: 1199px) {
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
  }

  @media (min-width: 600px) and (max-width: 899px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }

  @media (max-width: 599px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}

.audio-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;

  @media (min-width: 769px) {
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }
  }

  @media (max-width: 768px) {
    border-radius: 6px;
  }
}

.audio-cover {
  position: relative;
  aspect-ratio: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .no-cover {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.8);
  }
}

.audio-info {
  padding: 12px;

  @media (max-width: 768px) {
    padding: 8px;
  }
}

.audio-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #333;

  @media (max-width: 768px) {
    font-size: 12px;
    margin-bottom: 4px;
  }
}

.audio-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;

  @media (max-width: 768px) {
    font-size: 10px;
  }
}

.pagination {
  display: flex;
  justify-content: center;

  @media (max-width: 768px) {
    :deep(.el-pagination) {
      flex-wrap: wrap;
      justify-content: center;
    }
  }
}
</style>
