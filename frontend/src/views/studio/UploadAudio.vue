<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">上传音频</h2>
      <router-link to="/studio/audios" class="text-blue-600 hover:text-blue-700">返回音频管理</router-link>
    </div>

    <div class="card p-6 max-w-2xl">
      <form @submit.prevent="handleUpload" class="space-y-6">
        <!-- Upload Mode -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">上传方式</label>
          <div class="flex gap-4">
            <label class="flex items-center">
              <input v-model="uploadMode" type="radio" value="file" class="mr-2" />
              <span>本地上传</span>
            </label>
            <label class="flex items-center">
              <input v-model="uploadMode" type="radio" value="url" class="mr-2" />
              <span>网络链接</span>
            </label>
          </div>
        </div>

        <!-- File Upload -->
        <div v-if="uploadMode === 'file'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">音频文件</label>
          <div class="border-2 border-dashed border-gray-300 dark:border-slate-600 rounded-lg p-6 text-center cursor-pointer hover:border-blue-500"
            @click="$refs.fileInput.click()"
            @drop.prevent="handleDrop"
            @dragover.prevent>
            <input ref="fileInput" type="file" accept="audio/*" @change="handleFileChange" class="hidden" />
            <MusicalNoteIcon class="w-12 h-12 mx-auto text-gray-400 mb-2" />
            <p class="text-gray-600 dark:text-gray-400">拖拽音频或点击上传</p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">支持 mp3、wav、flac 等格式</p>
          </div>
          <p v-if="selectedFile" class="mt-2 text-sm text-gray-600 dark:text-gray-400">已选择: {{ selectedFile.name }}</p>
        </div>

        <!-- URL Input -->
        <div v-else>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">音频链接</label>
          <input v-model="form.audio_url" type="url" placeholder="输入音频链接" class="input-field" required />
        </div>

        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">音频标题</label>
          <input v-model="form.title" type="text" placeholder="输入音频标题" class="input-field" required />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">音频描述</label>
          <textarea v-model="form.description" placeholder="输入音频描述" class="input-field" rows="4"></textarea>
        </div>

        <!-- Cover Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">封面图片（可选）</label>
          <div class="flex items-start gap-4">
            <div class="flex-1">
              <input ref="coverInput" type="file" accept="image/*" @change="handleCoverChange" class="hidden" />
              <button type="button" @click="$refs.coverInput.click()"
                class="px-4 py-2 bg-gray-200 dark:bg-slate-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-slate-600 transition-colors">
                选择图片
              </button>
              <p v-if="selectedCover" class="mt-2 text-sm text-gray-600 dark:text-gray-400">{{ selectedCover.name }}</p>
            </div>
            <div v-if="coverPreview" class="w-32 h-20 bg-gray-100 dark:bg-slate-800 rounded-lg overflow-hidden">
              <img :src="coverPreview" alt="封面预览" class="w-full h-full object-cover" />
            </div>
          </div>
        </div>

        <!-- Submit -->
        <button type="submit" :disabled="loading" class="btn-primary w-full">
          {{ loading ? '上传中...' : '上传音频' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { userAudioApi } from '@/api'
import { MusicalNoteIcon } from '@heroicons/vue/24/solid'

const uploadMode = ref('file')
const selectedFile = ref<File | null>(null)
const selectedCover = ref<File | null>(null)
const coverPreview = ref<string | null>(null)
const loading = ref(false)
const form = ref({
  title: '',
  description: '',
  audio_url: ''
})

const handleFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  selectedFile.value = input.files?.[0] || null
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
  } else {
    coverPreview.value = null
  }
}

const handleDrop = (e: DragEvent) => {
  selectedFile.value = e.dataTransfer?.files?.[0] || null
}

const handleUpload = async () => {
  if (uploadMode.value === 'file' && !selectedFile.value) {
    alert('请选择音频文件')
    return
  }
  if (uploadMode.value === 'url' && !form.value.audio_url) {
    alert('请输入音频链接')
    return
  }

  loading.value = true
  try {
    if (uploadMode.value === 'file') {
      const formData = new FormData()
      formData.append('audio_file', selectedFile.value!)
      formData.append('title', form.value.title)
      formData.append('visibility', 'public')
      if (form.value.description) formData.append('description', form.value.description)
      if (selectedCover.value) formData.append('cover_file', selectedCover.value)
      await userAudioApi.uploadAudio(formData)
    } else {
      const formData = new FormData()
      formData.append('title', form.value.title)
      formData.append('audio_url', form.value.audio_url)
      formData.append('visibility', 'public')
      if (form.value.description) formData.append('description', form.value.description)
      if (selectedCover.value) formData.append('cover_file', selectedCover.value)
      await userAudioApi.addAudioByURL(formData)
    }
    alert('上传成功')
    form.value = { title: '', description: '', audio_url: '' }
    selectedFile.value = null
    selectedCover.value = null
    coverPreview.value = null
  } catch (error: any) {
    console.error('上传失败', error)
    const errorMsg = error.response?.data?.detail || error.message || '上传失败'
    alert('上传失败: ' + errorMsg)
  } finally {
    loading.value = false
  }
}
</script>