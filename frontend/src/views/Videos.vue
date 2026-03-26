<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">全部视频</h1>
        <p class="text-gray-600 dark:text-gray-400">发现更多精彩内容</p>
      </div>

      <!-- Search and Filter -->
      <div class="mb-8 space-y-4">
        <div class="flex gap-2">
          <input
            v-model="searchQuery"
            @keyup.enter="loadVideos"
            type="text"
            placeholder="搜索视频..."
            class="input-field flex-1"
          />
          <button @click="loadVideos" class="btn-primary">搜索</button>
        </div>

        <!-- Category Filter -->
        <div class="flex gap-2 flex-wrap">
          <button
            @click="selectedCategory = null; loadVideos()"
            :class="[
              'px-4 py-2 rounded-lg transition-colors',
              selectedCategory === null
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-slate-700 text-gray-900 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-slate-600'
            ]"
          >
            全部
          </button>
          <button
            v-for="category in categories"
            :key="category.id"
            @click="selectedCategory = category.id; loadVideos()"
            :class="[
              'px-4 py-2 rounded-lg transition-colors',
              selectedCategory === category.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-slate-700 text-gray-900 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-slate-600'
            ]"
          >
            {{ category.name }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <!-- Video Grid -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div
          v-for="video in videos"
          :key="video.id"
          @click="$router.push(`/video/${video.id}`)"
          class="card card-hover group"
        >
          <div class="relative aspect-video bg-gray-200 dark:bg-slate-800 overflow-hidden">
            <img
              v-if="video.cover_url"
              :src="getFullUrl(video.cover_url)"
              :alt="video.title"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
              <FilmIcon class="w-12 h-12" />
            </div>
            <div class="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
              {{ formatDuration(video.duration) }}
            </div>
          </div>
          <div class="p-4">
            <h3 class="font-semibold text-gray-900 dark:text-white line-clamp-2 mb-2">{{ video.title }}</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">{{ video.uploader?.username || '未知' }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-500">{{ video.views }} 次播放</p>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && videos.length === 0" class="text-center py-12">
        <p class="text-gray-600 dark:text-gray-400">暂无视频</p>
      </div>

      <!-- Pagination -->
      <div v-if="videos.length > 0" class="flex justify-center items-center gap-4">
        <button
          @click="page > 1 && (page--, loadVideos())"
          :disabled="page === 1"
          class="px-4 py-2 bg-gray-200 dark:bg-slate-700 text-gray-900 dark:text-gray-100 rounded-lg disabled:opacity-50"
        >
          上一页
        </button>
        <span class="text-gray-600 dark:text-gray-400">第 {{ page }} 页</span>
        <button
          @click="page++, loadVideos()"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { videoApi, categoryApi } from '@/api'
import { useUserStore } from '@/store/user'
import Navbar from '@/components/Navbar.vue'
import { FilmIcon } from '@heroicons/vue/24/solid'
import type { Video, Category } from '@/types'

const userStore = useUserStore()

const getFullUrl = (url: string | undefined) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return url
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

const videos = ref<Video[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref<number | null>(null)
const page = ref(1)
const pageSize = 12

const loadCategories = async () => {
  try {
    categories.value = await categoryApi.getCategories()
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

const loadVideos = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize }
    if (selectedCategory.value) params.category_id = selectedCategory.value
    if (searchQuery.value) params.search = searchQuery.value
    const data = await videoApi.getVideos(params)
    videos.value = data.data || data
  } catch (error) {
    console.error('加载视频失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadVideos()
})
</script>
