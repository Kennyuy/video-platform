<template>
  <nav class="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2 font-bold text-xl text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
          <div class="w-8 h-8 bg-blue-600 dark:bg-blue-400 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-white dark:text-slate-900" viewBox="0 0 20 20" fill="currentColor">
              <path d="M6.3 2.841A1.5 1.5 0 004 4.11v11.78a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
            </svg>
          </div>
          VideoHub
        </router-link>

        <!-- Nav Links -->
        <div class="hidden md:flex items-center gap-8">
          <router-link to="/videos" class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            视频
          </router-link>
          <router-link to="/audios" class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            音频
          </router-link>
        </div>

        <!-- Right Actions -->
        <div class="flex items-center gap-4">
          <!-- Theme Toggle -->
          <button @click="toggleTheme" class="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors">
            <MoonIcon v-if="!isDark" class="w-5 h-5 text-gray-700" />
            <SunIcon v-else class="w-5 h-5 text-yellow-400" />
          </button>

          <!-- User Menu -->
          <div v-if="userStore.user" class="flex items-center gap-4">
            <div class="text-right">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ userStore.user.username }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ userStore.user.coins }} 硬币</p>
            </div>
            <button @click="showMenu = !showMenu" class="relative">
              <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                {{ userStore.user.username.charAt(0).toUpperCase() }}
              </div>
              <div v-if="showMenu" class="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-gray-200 dark:border-slate-700">
                <router-link to="/studio" class="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700">
                  创作中心
                </router-link>
                <router-link v-if="userStore.user.role === 'admin'" to="/admin" class="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700">
                  管理后台
                </router-link>
                <button @click="logout" class="w-full text-center px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700">
                  退出登录
                </button>
              </div>
            </button>
          </div>

          <!-- Auth Links -->
          <div v-else class="flex items-center gap-2">
            <router-link to="/login" class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
              登录
            </router-link>
            <router-link to="/register" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
              注册
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { MoonIcon, SunIcon } from '@heroicons/vue/24/solid'

const router = useRouter()
const userStore = useUserStore()
const showMenu = ref(false)
const isDark = ref(document.documentElement.classList.contains('dark'))

const toggleTheme = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>
