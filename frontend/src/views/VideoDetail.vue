<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">
    <Navbar />

    <div v-if="loading" class="flex justify-center items-center h-96">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="video" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content -->
        <div class="lg:col-span-2">
          <!-- Player -->
          <div ref="playerRef" class="w-full aspect-video bg-black rounded-lg mb-6"></div>

          <!-- Video Info -->
          <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">{{ video.title }}</h1>
            <p class="text-gray-600 dark:text-gray-400 mb-6">{{ video.description }}</p>

            <!-- Uploader Info -->
            <div class="flex items-center gap-4 pb-6 border-b border-gray-200 dark:border-slate-700">
              <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                {{ video.uploader?.username?.charAt(0).toUpperCase() || '?' }}
              </div>
              <div>
                <p class="font-semibold text-gray-900 dark:text-white">{{ video.uploader?.username || '未知' }}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ formatDate(video.created_at) }}</p>
              </div>
            </div>

            <!-- Stats -->
            <div class="flex gap-8 py-6 border-b border-gray-200 dark:border-slate-700">
              <div>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ video.views }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">次播放</p>
              </div>
              <div>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ video.likes }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">次点赞</p>
              </div>
              <div>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ video.favorites }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">次收藏</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div>
          <!-- Interaction Buttons -->
          <div class="space-y-3 mb-8">
            <button
              @click="toggleLike"
              :class="[
                'w-full py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2',
                isLiked
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-gray-200 dark:bg-slate-700 text-gray-900 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-slate-600'
              ]"
            >
              <HeartIcon class="w-5 h-5" />
              {{ isLiked ? '已点赞' : '点赞' }}
            </button>

            <button
              v-if="userStore.isLoggedIn()"
              @click="toggleCoin"
              :class="[
                'w-full py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2',
                isCoinedOut
                  ? 'bg-gray-300 dark:bg-slate-600 text-gray-600 dark:text-gray-400 cursor-not-allowed'
                  : 'bg-yellow-500 hover:bg-yellow-600 text-white'
              ]"
              :disabled="isCoinedOut"
            >
              <CurrencyYenIcon class="w-5 h-5" />
              {{ isCoinedOut ? '已投币' : '投币' }}
            </button>

            <button
              @click="toggleFavorite"
              :class="[
                'w-full py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2',
                isFavorited
                  ? 'bg-blue-500 hover:bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-slate-700 text-gray-900 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-slate-600'
              ]"
            >
              <BookmarkIcon class="w-5 h-5" />
              {{ isFavorited ? '已收藏' : '收藏' }}
            </button>

            <button
              @click="shareVideo"
              class="w-full py-3 rounded-lg font-semibold bg-gray-200 dark:bg-slate-700 text-gray-900 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-slate-600 transition-colors flex items-center justify-center gap-2"
            >
              <ShareIcon class="w-5 h-5" />
              分享
            </button>
          </div>

          <!-- Coin Balance -->
          <div v-if="userStore.isLoggedIn()" class="card p-4 mb-8">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">硬币余额</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ userStore.user?.coins || 0 }}</p>
          </div>

          <!-- Login Prompt -->
          <div v-else class="card p-4 text-center">
            <p class="text-gray-600 dark:text-gray-400 mb-4">登录后可进行互动</p>
            <router-link to="/login" class="btn-primary w-full">登录</router-link>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-gray-600 dark:text-gray-400">视频不存在</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { videoApi } from '@/api'
import { useUserStore } from '@/store/user'
import Navbar from '@/components/Navbar.vue'
import DPlayer from 'dplayer'
import { HeartIcon, CurrencyYenIcon, BookmarkIcon, ShareIcon } from '@heroicons/vue/24/solid'
import type { Video } from '@/types'

const route = useRoute()
const userStore = useUserStore()
const playerRef = ref<HTMLElement>()

const video = ref<Video | null>(null)
const loading = ref(true)
const isLiked = ref(false)
const isCoinedOut = ref(false)
const isFavorited = ref(false)

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

const loadVideo = async () => {
  loading.value = true
  try {
    const id = route.params.id as string
    video.value = await videoApi.getVideoDetail(parseInt(id))

    // Record view
    await videoApi.incrementViews(parseInt(id))

    // Load interaction status
    if (userStore.isLoggedIn()) {
      const interactions = await videoApi.getInteractions(parseInt(id))
      isLiked.value = interactions.user_liked
      isCoinedOut.value = interactions.user_coins > 0
      isFavorited.value = interactions.user_favorited
    }
  } catch (error) {
    console.error('加载视频失败', error)
  } finally {
    loading.value = false
  }

  // Initialize player after DOM is ready
  await nextTick()
  if (playerRef.value && video.value?.video_url) {
    new DPlayer({
      container: playerRef.value,
      video: {
        url: video.value.video_url,
        pic: video.value.cover_url || undefined,
        type: 'auto'
      }
    })
  }
}

const toggleLike = async () => {
  if (!userStore.isLoggedIn()) {
    alert('请先登录')
    return
  }
  try {
    await videoApi.doInteraction(video.value!.id, 'like')
    isLiked.value = !isLiked.value
    video.value!.likes += isLiked.value ? 1 : -1
  } catch (error) {
    console.error('操作失败', error)
  }
}

const toggleCoin = async () => {
  if (!userStore.isLoggedIn()) {
    alert('请先登录')
    return
  }
  if (isCoinedOut.value) return
  try {
    await videoApi.doInteraction(video.value!.id, 'coin')
    isCoinedOut.value = true
    video.value!.coins += 1
    userStore.updateCoins((userStore.user?.coins || 0) - 1)
  } catch (error) {
    console.error('投币失败', error)
  }
}

const toggleFavorite = async () => {
  if (!userStore.isLoggedIn()) {
    alert('请先登录')
    return
  }
  try {
    await videoApi.doInteraction(video.value!.id, 'favorite')
    isFavorited.value = !isFavorited.value
    video.value!.favorites += isFavorited.value ? 1 : -1
  } catch (error) {
    console.error('操作失败', error)
  }
}

const shareVideo = () => {
  const url = window.location.href
  if (navigator.share) {
    navigator.share({
      title: video.value?.title,
      url: url
    })
  } else {
    alert('分享链接: ' + url)
  }
}

onMounted(() => {
  loadVideo()
})
</script>