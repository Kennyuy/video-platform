<template>
  <div class="studio-layout">
    <!-- 侧边栏 -->
    <aside class="studio-sidebar">
      <div class="studio-logo">
        <h2>创作中心</h2>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="studio-menu"
      >
        <el-sub-menu index="video">
          <template #title>
            <el-icon><VideoCamera /></el-icon>
            <span>视频管理</span>
          </template>
          <el-menu-item index="/studio/upload">
            <el-icon><UploadFilled /></el-icon>
            <span>上传视频</span>
          </el-menu-item>
          <el-menu-item index="/studio/videos">
            <el-icon><List /></el-icon>
            <span>稿件管理</span>
          </el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="audio">
          <template #title>
            <el-icon><Headset /></el-icon>
            <span>音频管理</span>
          </template>
          <el-menu-item index="/studio/upload-audio">
            <el-icon><UploadFilled /></el-icon>
            <span>上传音频</span>
          </el-menu-item>
          <el-menu-item index="/studio/audios">
            <el-icon><List /></el-icon>
            <span>音频列表</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>

      <div class="studio-back">
        <el-button link @click="$router.push('/')">
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </el-button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="studio-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { UploadFilled, VideoCamera, Headset, List, ArrowLeft } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.studio-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f5f5;
}

.studio-sidebar {
  width: 220px;
  background: #fff;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.studio-logo {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;

  h2 {
    margin: 0;
    color: #00a1d6;
    font-size: 20px;
  }
}

.studio-menu {
  flex: 1;
  border-right: none;
}

.studio-back {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.studio-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>
