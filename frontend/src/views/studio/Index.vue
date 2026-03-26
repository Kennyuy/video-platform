<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="flex gap-8">
        <!-- Sidebar -->
        <div class="w-48">
          <nav class="space-y-2">
            <router-link to="/studio/videos" class="block px-4 py-2 rounded-lg text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800">
              视频管理
            </router-link>
            <router-link to="/studio/upload" class="block px-4 py-2 rounded-lg text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800">
              上传视频
            </router-link>
            <router-link to="/studio/audios" class="block px-4 py-2 rounded-lg text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800">
              音频管理
            </router-link>
            <router-link to="/studio/upload-audio" class="block px-4 py-2 rounded-lg text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800">
              上传音频
            </router-link>
          </nav>
        </div>

        <!-- Content -->
        <div class="flex-1">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Navbar from '@/components/Navbar.vue'
</script>
