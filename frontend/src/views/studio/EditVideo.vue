<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">编辑视频</h2>
      <router-link to="/studio/videos" class="text-blue-600 hover:text-blue-700">返回稿件管理</router-link>
    </div>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="video" class="card p-6 max-w-2xl">
      <form @submit.prevent="handleUpdate" class="space-y-6">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">视频标题</label>
          <input v-model="form.title" type="text" placeholder="输入视频标题" class="input-field" required />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">视频描述</label>
          <textarea v-model="form.description" placeholder="输入视频描述" class="input-field" rows="4"></textarea>
        </div>

        <!-- Cover Preview & Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">视频封面</label>
          <div class="flex items-start gap-4">
            <div class="flex-1">
              <input ref="coverInput" type="file" accept="image/*" @change="handleCoverChange" class="hidden" />
              <button type="button" @click="$refs.coverInput.click()"
                class="px-4 py-2 bg-gray-200 dark:bg-slate-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-slate-600 transition-colors">
                更换封面
              </button>
              <p v-if="selectedCover" class="mt-2 text-sm text-gray-600 dark:text-gray-400">{{ selectedCover.name }}</p>
            </div>
            <div class="w-40 h-24 bg-gray-100 dark:bg-slate-800 rounded-lg overflow-hidden">
              <img v-if="coverPreview || video.cover_url" :src="coverPreview || video.cover_url" alt="封面预览" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                无封面
              </div>
            </div>
          </div>
        </div>

        <!-- Visibility -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">可见性</label>
          <select v-model="form.visibility" class="input-field">
            <option value="public">公开</option>
            <option value="private">私密</option>
          </select>
        </div>

        <!-- Submit -->
        <div class="flex gap-4">
          <button type="submit" :disabled="saving" class="btn-primary flex-1">
            {{ saving ? '保存中...' : '保存修改' }}
          </button>
          <button type="button" @click="handleDelete" class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors">
            删除视频
          </button>
        </div>
      </form>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-gray-600 dark:text-gray-400">视频不存在或无权访问</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { userVideoApi } from '@/api'
import type { Video } from '@/types'

const route = useRoute()
const router = useRouter()

const video = ref<Video | null>(null)
const loading = ref(true)
const saving = ref(false)
const selectedCover = ref<File | null>(null)
const coverPreview = ref<string | null>(null)

const form = ref({
  title: '',
  description: '',
  visibility: 'public'
})

const loadVideo = async () => {
  loading.value = true
  try {
    const id = parseInt(route.params.id as string)
    video.value = await userVideoApi.getVideoDetail(id)
    form.value.title = video.value.title
    form.value.description = video.value.description || ''
    form.value.visibility = video.value.visibility
  } catch (error) {
    console.error('加载视频失败', error)
  } finally {
    loading.value = false
  }
}

const handleCoverChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  selectedCover.value = input.files?.[0] || null
  if (selectedCover.value) {
    const reader = new FileReader()
    reader.onload = (ev) => {
      coverPreview.value = ev.target?.result as string
    }
    reader.readAsDataURL(selectedCover.value)
  }
}

const handleUpdate = async () => {
  saving.value = true
  try {
    const formData = new FormData()
    formData.append('title', form.value.title)
    if (form.value.description) formData.append('description', form.value.description)
    formData.append('visibility', form.value.visibility)
    if (selectedCover.value) formData.append('cover_file', selectedCover.value)

    // 使用 fetch 直接发送 PUT 请求
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/user/videos/${video.value!.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })

    if (!response.ok) {
      throw new Error('更新失败')
    }

    alert('保存成功')
    router.push('/studio/videos')
  } catch (error) {
    console.error('保存失败', error)
    alert('保存失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('确定要删除这个视频吗？此操作不可恢复。')) return

  try {
    await userVideoApi.deleteVideo(video.value!.id)
    alert('删除成功')
    router.push('/studio/videos')
  } catch (error) {
    console.error('删除失败', error)
    alert('删除失败')
  }
}

onMounted(() => {
  loadVideo()
})
</script>