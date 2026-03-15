<template>
  <div class="videos-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>视频管理</span>
          <el-button type="primary" @click="$router.push('/admin/upload')">
            <el-icon><Plus /></el-icon>
            上传视频
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索视频标题"
          :prefix-icon="Search"
          clearable
          style="width: 300px"
          @keyup.enter="loadVideos"
        />
        <el-select
          v-model="selectedStatus"
          placeholder="选择状态"
          clearable
          style="width: 150px"
          @change="loadVideos"
        >
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
          <el-option label="已归档" value="archived" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="loadVideos">搜索</el-button>
      </div>

      <!-- 视频列表 -->
      <el-table v-loading="loading" :data="videos" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="封面" width="120">
          <template #default="{ row }">
            <el-image
              v-if="row.cover_url"
              :src="getFullUrl(row.cover_url)"
              fit="cover"
              style="width: 100px; height: 56px; border-radius: 4px"
            />
            <div v-else class="no-cover">无封面</div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="uploader.username" label="上传者" width="120" />
        <el-table-column label="时长" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="views" label="播放量" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editVideo(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="primary" link @click="previewVideo(row)">
              <el-icon><View /></el-icon>
              预览
            </el-button>
            <el-popconfirm
              title="确定要删除这个视频吗？"
              @confirm="deleteVideo(row.id)"
            >
              <template #reference>
                <el-button type="danger" link>
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadVideos"
          @size-change="loadVideos"
        />
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑视频"
      width="600px"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="封面URL">
          <el-input v-model="editForm.cover_url" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status">
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Edit, View, Delete } from '@element-plus/icons-vue'
import { videoApi } from '@/api'
import type { Video } from '@/types'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 获取完整的资源 URL
const getFullUrl = (url: string | undefined) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return url
}

const videos = ref<Video[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedStatus = ref<string | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const editDialogVisible = ref(false)
const saving = ref(false)
const currentEditId = ref<number | null>(null)
const editForm = reactive({
  title: '',
  description: '',
  cover_url: '',
  status: 'published'
})

// 格式化时长
const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    published: 'success',
    draft: 'info',
    archived: 'warning'
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    published: '已发布',
    draft: '草稿',
    archived: '已归档'
  }
  return map[status] || status
}

// 加载视频列表
const loadVideos = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (selectedStatus.value) {
      params.status = selectedStatus.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    videos.value = await videoApi.adminGetVideos(params)
    total.value = videos.value.length
  } catch (error) {
    console.error('加载视频失败', error)
  } finally {
    loading.value = false
  }
}

// 编辑视频
const editVideo = (video: Video) => {
  currentEditId.value = video.id
  editForm.title = video.title
  editForm.description = video.description || ''
  editForm.cover_url = video.cover_url || ''
  editForm.status = video.status
  editDialogVisible.value = true
}

// 保存编辑
const saveEdit = async () => {
  if (!currentEditId.value) return

  saving.value = true
  try {
    await videoApi.updateVideo(currentEditId.value, editForm)
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    loadVideos()
  } catch (error) {
    console.error('保存失败', error)
  } finally {
    saving.value = false
  }
}

// 预览视频
const previewVideo = (video: Video) => {
  window.open(`/video/${video.id}`, '_blank')
}

// 删除视频
const deleteVideo = async (id: number) => {
  try {
    await videoApi.deleteVideo(id)
    ElMessage.success('删除成功')
    loadVideos()
  } catch (error) {
    console.error('删除失败', error)
  }
}

onMounted(() => {
  loadVideos()
})
</script>

<style scoped lang="scss">
.videos-manage {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
  }

  .no-cover {
    width: 100px;
    height: 56px;
    background: #f0f0f0;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #999;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
}
</style>
