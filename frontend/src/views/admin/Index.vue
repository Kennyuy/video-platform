<template>
  <el-container class="admin-container">
    <!-- 侧边栏 -->
    <el-aside width="240px" class="admin-aside">
      <div class="aside-header">
        <el-icon :size="24"><VideoPlay /></el-icon>
        <span>管理后台</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="admin-menu"
      >
        <el-menu-item index="/admin/videos">
          <el-icon><List /></el-icon>
          <span>视频管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/upload">
          <el-icon><UploadFilled /></el-icon>
          <span>上传视频</span>
        </el-menu-item>
      </el-menu>
      <div class="aside-footer">
        <el-button text @click="$router.push('/')">
          <el-icon><Back /></el-icon>
          返回前台
        </el-button>
      </div>
    </el-aside>

    <!-- 主体内容 -->
    <el-main class="admin-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { VideoPlay, List, UploadFilled, Back } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)
</script>

<style scoped lang="scss">
.admin-container {
  height: 100vh;
  background: #f5f7fa;
}

.admin-aside {
  background: #fff;
  display: flex;
  flex-direction: column;
}

.aside-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-color-primary);
  border-bottom: 1px solid #eee;
}

.admin-menu {
  flex: 1;
  border: none;
}

.aside-footer {
  padding: 16px;
  border-top: 1px solid #eee;
}

.admin-main {
  padding: 24px;
  overflow-y: auto;
}
</style>
