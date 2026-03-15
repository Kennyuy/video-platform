<template>
  <div class="upload-page">
    <el-card>
      <template #header>
        <span>上传视频</span>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <!-- 上传方式选择 -->
        <el-form-item label="上传方式">
          <el-radio-group v-model="uploadMode">
            <el-radio value="file">本地上传</el-radio>
            <el-radio value="url">网络链接</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 视频上传/链接 -->
        <el-form-item v-if="uploadMode === 'file'" label="视频文件" prop="video_file" required>
          <el-upload
            ref="videoUploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleVideoChange"
            accept="video/*"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将视频文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 mp4、mkv、avi、mov 格式，最大 500MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item v-else label="视频链接" prop="video_url" required>
          <el-input
            v-model="form.video_url"
            placeholder="请输入视频链接（如：https://example.com/video.mp4）"
          />
        </el-form-item>

        <!-- 封面上传 -->
        <el-form-item label="视频封面">
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
            建议尺寸 16:9，支持 jpg、jpeg、png、gif 格式
          </div>
        </el-form-item>

        <!-- 视频标题 -->
        <el-form-item label="视频标题" prop="title" required>
          <el-input
            v-model="form.title"
            placeholder="请输入视频标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <!-- 视频简介 -->
        <el-form-item label="视频简介">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入视频简介"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 视频分类 -->
        <el-form-item label="视频分类">
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
            选择"仅自己可见"后，视频将不会在公开列表中展示，只有你能查看
          </div>
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button type="primary" :loading="uploading" @click="handleSubmit">
            <el-icon><UploadFilled /></el-icon>
            {{ uploading ? '上传中...' : '立即上传' }}
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
import { videoApi, categoryApi } from '@/api'
import { useUserStore } from '@/store/user'
import type { FormInstance, FormRules, UploadFile, UploadUserFile } from 'element-plus'
import { ElMessage, type UploadProps } from 'element-plus'
import type { Category } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const videoUploadRef = ref()
const coverUploadRef = ref()
const uploadMode = ref<'file' | 'url'>('file')
const uploading = ref(false)

const form = reactive({
  title: '',
  description: '',
  category_id: undefined as number | undefined,
  video_url: '',
  visibility: 'public' as 'public' | 'private'
})

const videoFile = ref<File | null>(null)
const coverFile = ref<File | null>(null)
const categories = ref<Category[]>([])

const rules: FormRules = {
  title: [{ required: true, message: '请输入视频标题', trigger: 'blur' }],
  video_url: [{ required: true, message: '请输入视频链接', trigger: 'blur' }],
  video_file: [{ required: true, message: '请选择视频文件', trigger: 'change' }]
}

// 加载分类列表
const loadCategories = async () => {
  try {
    categories.value = await categoryApi.getCategories()
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

// 处理视频文件变化
const handleVideoChange: UploadProps['onChange'] = (uploadFile) => {
  if (uploadFile.raw) {
    // 验证文件大小
    const maxSize = 500 * 1024 * 1024 // 500MB
    if (uploadFile.size && uploadFile.size > maxSize) {
      ElMessage.error('文件大小不能超过 500MB')
      videoUploadRef.value?.clearFiles()
      return
    }

    // 验证文件类型
    const allowedTypes = ['video/mp4', 'video/mkv', 'video/avi', 'video/quicktime']
    if (!allowedTypes.includes(uploadFile.raw.type)) {
      ElMessage.error('不支持的文件类型')
      videoUploadRef.value?.clearFiles()
      return
    }

    videoFile.value = uploadFile.raw
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
  if (uploadMode.value === 'file' && !videoFile.value) {
    ElMessage.error('请选择视频文件')
    return
  }

  if (uploadMode.value === 'url' && !form.video_url) {
    ElMessage.error('请输入视频链接')
    return
  }

  if (!form.title) {
    ElMessage.error('请输入视频标题')
    return
  }

  uploading.value = true

  try {
    if (uploadMode.value === 'file') {
      // 文件上传
      await videoApi.uploadVideo({
        title: form.title,
        description: form.description,
        category_id: form.category_id,
        visibility: form.visibility,
        video_file: videoFile.value!,
        cover_file: coverFile.value
      })
    } else {
      // URL上传
      await videoApi.addVideoByURL({
        title: form.title,
        video_url: form.video_url,
        description: form.description,
        category_id: form.category_id,
        visibility: form.visibility
      })
    }

    ElMessage.success('上传成功')
    resetForm()
    router.push('/admin/videos')
  } catch (error) {
    console.error('上传失败', error)
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
  form.video_url = ''
  form.visibility = 'public'
  videoFile.value = null
  coverFile.value = null
  uploadMode.value = 'file'
  videoUploadRef.value?.clearFiles()
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
