<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">
    <Navbar />

    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-400 dark:from-blue-900 dark:to-blue-700 text-white py-16 md:py-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-4xl md:text-5xl font-bold mb-4">VideoHub</h1>
          <p class="text-lg md:text-xl text-blue-100 mb-8">发现、分享、享受精彩内容</p>
          <div class="flex gap-4 justify-center">
            <input
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              type="text"
              placeholder="搜索视频或音频..."
              class="input-field w-full max-w-md"
            />
            <button @click="handleSearch" class="btn-primary">搜索</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Category Filter -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex gap-2 flex-wrap">
        <button
          @click="selectedCategory = null; loadVideos(); loadAudios()"
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
          @click="selectedCategory = category.id; loadVideos(); loadAudios()"
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

    <!-- Videos Section -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="flex justify-between items-center mb-8">
        <h2 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">精选视频</h2>
        <router-link to="/videos" class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
          查看全部 →
        </router-link>
      </div>

      <div v-if="videoLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
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
    </div>

    <!-- Audios Section -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="flex justify-between items-center mb-8">
        <h2 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">精选音频</h2>
        <router-link to="/audios" class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
          查看全部 →
        </router-link>
      </div>

      <div v-if="audioLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div
          v-for="audio in audios"
          :key="audio.id"
          @click="$router.push(`/audio/${audio.id}`)"
          class="card card-hover group"
        >
          <div class="relative aspect-square bg-blue-600 overflow-hidden">
            <img
              v-if="audio.cover_url"
              :src="getFullUrl(audio.cover_url)"
              :alt="audio.title"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-white">
              <MusicalNoteIcon class="w-8 h-8" />
            </div>
          </div>
          <div class="p-3">
            <h3 class="font-semibold text-gray-900 dark:text-white line-clamp-2 text-sm mb-1">{{ audio.title }}</h3>
            <p class="text-xs text-gray-600 dark:text-gray-400">{{ audio.uploader?.username || '未知' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { videoApi, categoryApi, audioApi } from '@/api'
import { useUserStore } from '@/store/user'
import Navbar from '@/components/Navbar.vue'
import { FilmIcon, MusicalNoteIcon } from '@heroicons/vue/24/solid'
import type { Video, Category, Audio } from '@/types'

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
const audios = ref<Audio[]>([])
const categories = ref<Category[]>([])
const videoLoading = ref(false)
const audioLoading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref<number | null>(null)

const loadCategories = async () => {
  try {
    categories.value = await categoryApi.getCategories()
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

const loadVideos = async () => {
  videoLoading.value = true
  try {
    const params: any = { page: 1, page_size: 8 }
    if (selectedCategory.value) params.category_id = selectedCategory.value
    if (searchQuery.value) params.search = searchQuery.value
    const data = await videoApi.getVideos(params)
    videos.value = (data.data || data).slice(0, 8)
  } catch (error) {
    console.error('加载视频失败', error)
  } finally {
    videoLoading.value = false
  }
}

const loadAudios = async () => {
  audioLoading.value = true
  try {
    const params: any = { page: 1, page_size: 12 }
    if (selectedCategory.value) params.category_id = selectedCategory.value
    if (searchQuery.value) params.search = searchQuery.value
    const data = await audioApi.getAudios(params)
    audios.value = (data || []).slice(0, 12)
  } catch (error) {
    console.error('加载音频失败', error)
  } finally {
    audioLoading.value = false
  }
}

const handleSearch = () => {
  loadVideos()
  loadAudios()
}

onMounted(() => {
  loadCategories()
  loadVideos()
  loadAudios()
})
</script>
