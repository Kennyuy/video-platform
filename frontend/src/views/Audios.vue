<template>
  <el-container class="audios-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <el-icon :size="28"><Headset /></el-icon>
          <span>媒体平台</span>
        </div>
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索音频"
            :prefix-icon="Search"
            clearable
            @keyup.enter="loadAudios"
          >
            <template #append>
              <el-button :icon="Search" @click="loadAudios" />
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
          </template>
        </div>
      </div>
    </el-header>

    <!-- 主体内容 -->
    <el-main class="main-content">
      <div class="page-header">
        <h1><el-icon><Headset /></el-icon> 全部音频</h1>
      </div>

      <!-- 分类筛选 -->
      <div class="category-filter">
        <el-button
          v-for="category in categories"
          :key="category.id"
          :type="selectedCategory === category.id ? 'primary' : 'default'"
          size="small"
          @click="selectedCategory = category.id; loadAudios()"
        >
          {{ category.name }}
        </el-button>
        <el-button
          :type="selectedCategory === null ? 'primary' : 'default'"
          size="small"
          @click="selectedCategory = null; loadAudios()"
        >
          全部
        </el-button>
      </div>

      <!-- 音频列表 -->
      <div v-loading="loading" class="audio-grid">
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

      <el-empty v-if="!loading && audios.length === 0" description="暂无音频" />

      <!-- 分页 -->
      <div class="pagination" v-if="audios.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[6, 12, 24]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadAudios"
          @size-change="loadAudios"
        />
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Headset, Search, VideoCamera, Setting, SwitchButton, Coin } from '@element-plus/icons-vue'
import { audioApi, categoryApi } from '@/api'
import { useUserStore } from '@/store/user'
import type { Audio, Category } from '@/types'

const userStore = useUserStore()

// 获取完整的资源 URL
const getFullUrl = (url: string | undefined) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return url
}

const audios = ref<Audio[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(6)
const total = ref(0)

// 加载分类
const loadCategories = async () => {
  try {
    categories.value = await categoryApi.getCategories()
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

// 加载音频
const loadAudios = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const data = await audioApi.getAudios(params)
    audios.value = data || []
    total.value = audios.value.length
  } catch (error) {
    console.error('加载音频失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadAudios()
})
</script>

<style scoped lang="scss">
.audios-container {
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

.page-header {
  margin-bottom: 24px;

  @media (max-width: 768px) {
    margin-bottom: 16px;
  }

  h1 {
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