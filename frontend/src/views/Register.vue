<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-600 to-blue-400 dark:from-blue-900 dark:to-blue-700 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="bg-white dark:bg-slate-900 rounded-lg shadow-xl p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 6a2 2 0 012-2h12a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z"></path>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">注册</h1>
          <p class="text-gray-600 dark:text-gray-400 mt-2">加入 VideoHub 社区</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleRegister" class="space-y-4">
          <!-- Username -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">用户名</label>
            <input
              v-model="form.username"
              type="text"
              placeholder="输入用户名"
              class="input-field"
              required
            />
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">邮箱</label>
            <input
              v-model="form.email"
              type="email"
              placeholder="输入邮箱"
              class="input-field"
              required
            />
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">密码</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="输入密码"
              class="input-field"
              required
            />
          </div>

          <!-- Confirm Password -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">确认密码</label>
            <input
              v-model="form.confirmPassword"
              type="password"
              placeholder="确认密码"
              class="input-field"
              required
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" class="p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-lg text-sm">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors"
          >
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>

        <!-- Footer -->
        <div class="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          已有账号？
          <router-link to="/login" class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-semibold">
            立即登录
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)
const error = ref('')

const handleRegister = async () => {
  error.value = ''

  if (form.value.password !== form.value.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  try {
    await userStore.register(form.value.username, form.value.email, form.value.password)
    router.push('/login')
  } catch (err: any) {
    error.value = err.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>
