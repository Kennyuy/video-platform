<template>
  <div class="audios-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的音频</span>
          <el-button type="primary" @click="$router.push('/studio/upload-audio')">
            <el-icon><Plus /></el-icon>
            上传音频
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索音频标题"
          :prefix-icon="Search"
          clearable
          style="width: 300px"
          @keyup.enter="loadAudios"
        />
        <el-button @click="loadAudios">搜索</el-button>
      </div>

      <!-- 音频列表 -->
      <el-table :data="audios" v-loading="loading" stripe>
        <el-table-column label="封面" width="100">
          <template #default="{ row }">
            <div class="audio-cover">
              <img v-if="row.cover_url" :src="getFullUrl(row.cover_url)" :alt="row.title" />
              <div v-else class="no-cover">
                <el-icon><Headset /></el-icon>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="播放量" width="100">
          <template #default="{ row }">
            {{ formatNumber(row.plays) }}
          </template>
        </el-table-column>
        <el-table-column label="互动" width="150">
          <template #default="{ row }">
            <div class="interaction-info">
              <span><el-icon><Pointer /></el-icon> {{ row.likes }}</span>
              <span><el-icon><Coin /></el-icon> {{ row.coins }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="权限" width="100">
          <template #default="{ row }">
            <el-tag :type="row.visibility === 'public' ? 'success' : 'info'" size="small">
              {{ row.visibility === 'public' ? '公开' : '私密' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="上传时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewAudio(row.id)">
              查看
            </el-button>
            <el-button type="danger" link @click="deleteAudio(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadAudios"
          @size-change="loadAudios"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Headset, Pointer, Coin } from '@element-plus/icons-vue'
import { userAudioApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Audio } from '@/types'

const router = useRouter()

const audios = ref<Audio[]>([])
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 获取完整的资源 URL
const getFullUrl = (url: string | undefined) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return url
}

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 加载音频列表
const loadAudios = async () => {
  loading.value = true
  try {
    const data = await userAudioApi.getMyAudios({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined
    })
    audios.value = data
    total.value = data.length // 如果后端返回总数，使用 total
  } catch (error) {
    console.error('加载音频失败', error)
    ElMessage.error('加载音频失败')
  } finally {
    loading.value = false
  }
}

// 查看音频
const viewAudio = (id: number) => {
  router.push(`/audio/${id}`)
}

// 删除音频
const deleteAudio = async (audio: Audio) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除音频《${audio.title}》吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await userAudioApi.deleteAudio(audio.id)
    ElMessage.success('删除成功')
    loadAudios()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  loadAudios()
})
</script>

<style scoped lang="scss">
.audios-page {
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

  .audio-cover {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    overflow: hidden;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .no-cover {
      color: rgba(255, 255, 255, 0.8);
      font-size: 24px;
    }
  }

  .interaction-info {
    display: flex;
    gap: 8px;
    font-size: 12px;
    color: #666;

    span {
      display: flex;
      align-items: center;
      gap: 2px;
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
}
</style>