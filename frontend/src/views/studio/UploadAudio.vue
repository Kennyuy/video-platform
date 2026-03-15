<template>
  <div class="upload-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>上传音频</span>
          <el-button @click="$router.push('/studio/audios')">
            返回音频管理
          </el-button>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <!-- 上传方式选择 -->
        <el-form-item label="上传方式">
          <el-radio-group v-model="uploadMode">
            <el-radio value="file">本地上传</el-radio>
            <el-radio value="url">网络链接</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 音频上传/链接 -->
        <el-form-item v-if="uploadMode === 'file'" label="音频文件" prop="audio_file" required>
          <el-upload
            ref="audioUploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleAudioChange"
            accept="audio/*"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将音频文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 mp3、wav、flac、aac、ogg、m4a 格式，最大 500MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item v-else label="音频链接" prop="audio_url" required>
          <el-input
            v-model="form.audio_url"
            placeholder="请输入音频链接（如：https://example.com/audio.mp3）"
          />
        </el-form-item>

        <!-- 封面上传 -->
        <el-form-item label="音频封面">
          <el-upload
            ref="coverUploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleCoverChange"
            :on-remove="handleCoverRemove"
            accept="image/*"
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="el-upload__tip">
            建议尺寸 1:1，支持 jpg、jpeg、png、gif 格式
          </div>
        </el-form-item>

        <!-- 音频标题 -->
        <el-form-item label="音频标题" prop="title" required>
          <el-input
            v-model="form.title"
            placeholder="请输入音频标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <!-- 音频简介 -->
        <el-form-item label="音频简介">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入音频简介"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 音频分类 -->
        <el-form-item label="音频分类">
          <el-select
            v-model="form.category_id"
            placeholder="请选择分类"
            clearable
          >
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <!-- 浏览权限 -->
        <el-form-item label="浏览权限">
          <el-radio-group v-model="form.visibility">
            <el-radio value="public">所有人可见</el-radio>
            <el-radio value="private">仅自己可见</el-radio>
          </el-radio-group>
          <div class="el-upload__tip" style="margin-top: 4px;">
            选择"仅自己可见"后，音频将不会在公开列表中展示，只有你能查看
          </div>
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button type="primary" :loading="uploading" @click="handleSubmit">
            <el-icon><UploadFilled /></el-icon>
            {{ uploading ? '上传中...' : '立即投稿' }}
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, Plus } from '@element-plus/icons-vue'
import { userAudioApi, categoryApi } from '@/api'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import { ElMessage, type UploadProps } from 'element-plus'
import type { Category } from '@/types'

const router = useRouter()

const formRef = ref<FormInstance>()
const audioUploadRef = ref()
const coverUploadRef = ref()
const uploadMode = ref<'file' | 'url'>('file')
const uploading = ref(false)

const form = reactive({
  title: '',
  description: '',
  category_id: undefined as number | undefined,
  audio_url: '',
  visibility: 'public' as 'public' | 'private'
})

const audioFile = ref<File | null>(null)
const coverFile = ref<File | null>(null)
const categories = ref<Category[]>([])

const rules: FormRules = {
  title: [{ required: true, message: '请输入音频标题', trigger: 'blur' }],
  audio_url: [{ required: true, message: '请输入音频链接', trigger: 'blur' }],
  audio_file: [{ required: true, message: '请选择音频文件', trigger: 'change' }]
}

// 加载分类列表
const loadCategories = async () => {
  try {
    categories.value = await categoryApi.getCategories()
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

// 处理音频文件变化
const handleAudioChange = (uploadFile: UploadFile) => {
  if (uploadFile.raw) {
    // 验证文件大小
    const maxSize = 500 * 1024 * 1024 // 500MB
    if (uploadFile.size && uploadFile.size > maxSize) {
      ElMessage.error('文件大小不能超过 500MB')
      audioUploadRef.value?.clearFiles()
      return
    }

    // 验证文件类型
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/ogg', 'audio/mp4', 'audio/x-m4a']
    if (uploadFile.raw.type && !allowedTypes.includes(uploadFile.raw.type)) {
      ElMessage.warning('建议使用 mp3 格式以获得最佳兼容性')
    }

    audioFile.value = uploadFile.raw
  }
}

// 处理封面文件变化
const handleCoverChange: UploadProps['onChange'] = (uploadFile) => {
  if (uploadFile.raw) {
    coverFile.value = uploadFile.raw
  }
}

// 处理封面移除
const handleCoverRemove = () => {
  coverFile.value = null
}

// 提交上传
const handleSubmit = async () => {
  if (!formRef.value) return

  // 验证表单
  if (uploadMode.value === 'file' && !audioFile.value) {
    ElMessage.error('请选择音频文件')
    return
  }

  if (uploadMode.value === 'url' && !form.audio_url) {
    ElMessage.error('请输入音频链接')
    return
  }

  if (!form.title) {
    ElMessage.error('请输入音频标题')
    return
  }

  uploading.value = true

  try {
    if (uploadMode.value === 'file') {
      // 文件上传
      await userAudioApi.uploadAudio({
        title: form.title,
        description: form.description,
        category_id: form.category_id,
        visibility: form.visibility,
        audio_file: audioFile.value!,
        cover_file: coverFile.value
      })
    } else {
      // URL上传
      await userAudioApi.addAudioByURL({
        title: form.title,
        audio_url: form.audio_url,
        description: form.description,
        category_id: form.category_id,
        visibility: form.visibility,
        cover_file: coverFile.value
      })
    }

    ElMessage.success('投稿成功')
    resetForm()
    router.push('/studio/audios')
  } catch (error: any) {
    console.error('上传失败', error)
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  form.title = ''
  form.description = ''
  form.category_id = undefined
  form.audio_url = ''
  form.visibility = 'public'
  audioFile.value = null
  coverFile.value = null
  uploadMode.value = 'file'
  audioUploadRef.value?.clearFiles()
  coverUploadRef.value?.clearFiles()
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped lang="scss">
.upload-page {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-upload-list__item) {
  transition: none;
}

.el-icon--upload {
  font-size: 48px;
  color: var(--el-text-color-secondary);
}
</style>