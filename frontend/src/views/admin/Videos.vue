<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">视频管理</h1>
        <router-link to="/admin/upload" class="btn-primary">上传视频</router-link>
      </div>

      <!-- Search -->
      <div class="mb-6 flex gap-2">
        <input
          v-model="searchQuery"
          @keyup.enter="loadVideos"
          type="text"
          placeholder="搜索视频..."
          class="input-field flex-1"
        />
        <button @click="loadVideos" class="btn-primary">搜索</button>
      </div>

      <!-- Table -->
      <div class="card overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-100 dark:bg-slate-800">
            <tr>
              <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">标题</th>
              <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">上传者</th>
              <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">播放量</th>
              <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">状态</th>
              <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-slate-700">
            <tr v-for="video in videos" :key="video.id" class="hover:bg-gray-50 dark:hover:bg-slate-800">
              <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">{{ video.title }}</td>
              <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">{{ video.uploader?.username }}</td>
              <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">{{ video.views }}</td>
              <td class="px-6 py-4 text-sm">
                <span :class="[
                  'px-2 py-1 rounded text-xs font-semibold',
                  video.status === 'published' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                ]">
                  {{ video.status }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm">
                <button @click="deleteVideo(video.id)" class="text-red-600 hover:text-red-700 dark:text-red-400">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { videoApi } from '@/api'
import Navbar from '@/components/Navbar.vue'
import type { Video } from '@/types'

const videos = ref<Video[]>([])
const searchQuery = ref('')

const loadVideos = async () => {
  try {
    const params: any = { page: 1, page_size: 50 }
    if (searchQuery.value) params.search = searchQuery.value
    const data = await videoApi.getVideos(params)
    videos.value = data.data || data
  } catch (error) {
    console.error('加载视频失败', error)
  }
}

const deleteVideo = async (id: number) => {
  if (!confirm('确定删除此视频？')) return
  try {
    await videoApi.deleteVideo(id)
    loadVideos()
  } catch (error) {
    console.error('删除失败', error)
  }
}

onMounted(() => {
  loadVideos()
})
</script>
