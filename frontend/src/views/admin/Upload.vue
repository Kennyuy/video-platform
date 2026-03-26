<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">上传视频</h2>

    <div class="card p-6 max-w-2xl">
      <form @submit.prevent="handleUpload" class="space-y-6">
        <!-- Upload Mode -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">上传方式</label>
          <div class="flex gap-4">
            <label class="flex items-center">
              <input v-model="uploadMode" type="radio" value="file" class="mr-2" />
              <span class="text-gray-700 dark:text-gray-300">本地上传</span>
            </label>
            <label class="flex items-center">
              <input v-model="uploadMode" type="radio" value="url" class="mr-2" />
              <span class="text-gray-700 dark:text-gray-300">网络链接</span>
            </label>
          </div>
        </div>

        <!-- File Upload -->
        <div v-if="uploadMode === 'file'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">视频文件</label>
          <div class="border-2 border-dashed border-gray-300 dark:border-slate-600 rounded-lg p-6 text-center cursor-pointer hover:border-blue-500"
            @click="$refs.fileInput.click()"
            @drop.prevent="handleDrop"
            @dragover.prevent>
            <input ref="fileInput" type="file" accept="video/*" @change="handleFileChange" class="hidden" />
            <svg class="w-12 h-12 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            <p class="text-gray-600 dark:text-gray-400">拖拽视频或点击上传</p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">支持 mp4、mkv、avi、mov，最大 500MB</p>
          </div>
          <p v-if="selectedFile" class="mt-2 text-sm text-gray-600 dark:text-gray-400">已选择: {{ selectedFile.name }}</p>
        </div>

        <!-- URL Input -->
        <div v-else>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">视频链接</label>
          <input v-model="form.video_url" type="url" placeholder="输入视频链接" class="input-field" required />
        </div>

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

        <!-- Category -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">分类</label>
          <select v-model="form.category_id" class="input-field" required>
            <option value="">选择分类</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>

        <!-- Submit -->
        <button type="submit" :disabled="loading" class="btn-primary w-full">
          {{ loading ? '上传中...' : '上传视频' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { videoApi, categoryApi } from '@/api'
import type { Category } from '@/types'

const uploadMode = ref('file')
const selectedFile = ref<File | null>(null)
const categories = ref<Category[]>([])
const loading = ref(false)
const form = ref({
  title: '',
  description: '',
  category_id: '',
  video_url: ''
})

const handleFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  selectedFile.value = input.files?.[0] || null
}

const handleDrop = (e: DragEvent) => {
  selectedFile.value = e.dataTransfer?.files?.[0] || null
}

const handleUpload = async () => {
  if (uploadMode.value === 'file' && !selectedFile.value) {
    alert('请选择视频文件')
    return
  }
  if (uploadMode.value === 'url' && !form.value.video_url) {
    alert('请输入视频链接')
    return
  }

  loading.value = true
  try {
    if (uploadMode.value === 'file') {
      const formData = new FormData()
      formData.append('file', selectedFile.value!)
      formData.append('title', form.value.title)
      formData.append('description', form.value.description)
      formData.append('category_id', form.value.category_id)
      await videoApi.uploadVideo(formData)
    } else {
      await videoApi.addVideoByUrl({
        title: form.value.title,
        description: form.value.description,
        category_id: parseInt(form.value.category_id),
        video_source: form.value.video_url
      })
    }
    alert('上传成功')
    form.value = { title: '', description: '', category_id: '', video_url: '' }
    selectedFile.value = null
  } catch (error) {
    console.error('上传失败', error)
    alert('上传失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    categories.value = await categoryApi.getCategories()
  } catch (error) {
    console.error('加载分类失败', error)
  }
})
</script>
