<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">稿件管理</h2>
      <router-link to="/studio/upload" class="btn-primary">上传视频</router-link>
    </div>

    <div class="card">
      <!-- Search & Filter -->
      <div class="p-4 border-b border-gray-200 dark:border-slate-700 flex gap-2 flex-wrap">
        <input v-model="searchQuery" @keyup.enter="loadVideos" type="text" placeholder="搜索..." class="input-field flex-1 min-w-[200px]" />
        <select v-model="selectedStatus" @change="loadVideos" class="input-field w-32">
          <option value="">全部状态</option>
          <option value="published">已发布</option>
          <option value="draft">草稿</option>
          <option value="archived">已归档</option>
        </select>
        <select v-model="selectedVisibility" @change="loadVideos" class="input-field w-32">
          <option value="">全部可见性</option>
          <option value="public">公开</option>
          <option value="private">私密</option>
        </select>
        <button @click="loadVideos" class="btn-primary">搜索</button>
      </div>

      <!-- Table -->
      <table class="w-full">
        <thead class="bg-gray-100 dark:bg-slate-800">
          <tr>
            <th class="px-6 py-3 text-left text-sm font-semibold">标题</th>
            <th class="px-6 py-3 text-left text-sm font-semibold">状态</th>
            <th class="px-6 py-3 text-left text-sm font-semibold">可见性</th>
            <th class="px-6 py-3 text-left text-sm font-semibold">播放量</th>
            <th class="px-6 py-3 text-left text-sm font-semibold">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-slate-700">
          <tr v-for="video in videos" :key="video.id" class="hover:bg-gray-50 dark:hover:bg-slate-800">
            <td class="px-6 py-4 text-sm">{{ video.title }}</td>
            <td class="px-6 py-4 text-sm">
              <span :class="['px-2 py-1 rounded text-xs font-semibold', video.status === 'published' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200']">
                {{ video.status === 'published' ? '已发布' : video.status }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm">
              <span :class="['px-2 py-1 rounded text-xs font-semibold', video.visibility === 'public' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200']">
                {{ video.visibility === 'public' ? '公开' : '私密' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm">{{ video.views }}</td>
            <td class="px-6 py-4 text-sm space-x-2">
              <button @click="editVideo(video.id)" class="text-blue-600 hover:text-blue-700">编辑</button>
              <button @click="deleteVideo(video.id)" class="text-red-600 hover:text-red-700">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userVideoApi } from '@/api'
import type { Video } from '@/types'

const router = useRouter()
const videos = ref<Video[]>([])
const searchQuery = ref('')
const selectedStatus = ref('')
const selectedVisibility = ref('')

const loadVideos = async () => {
  try {
    const params: any = { page: 1, page_size: 50 }
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedStatus.value) params.status = selectedStatus.value
    if (selectedVisibility.value) params.visibility = selectedVisibility.value
    videos.value = await userVideoApi.getMyVideos(params)
  } catch (error) {
    console.error('加载视频失败', error)
  }
}

const editVideo = (id: number) => {
  router.push(`/studio/videos/${id}/edit`)
}

const deleteVideo = async (id: number) => {
  if (!confirm('确定删除？')) return
  try {
    await userVideoApi.deleteVideo(id)
    loadVideos()
  } catch (error) {
    console.error('删除失败', error)
  }
}

onMounted(() => {
  loadVideos()
})
</script>
