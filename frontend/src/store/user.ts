import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userApi } from '@/api'
import type { User, LoginResponse } from '@/types'
import toast from '@/utils/toast'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  // 初始化用户信息
  const initUser = async () => {
    if (token.value) {
      try {
        const userData = await userApi.getMe()
        user.value = userData
        localStorage.setItem('user', JSON.stringify(userData))
      } catch (error) {
        console.error('获取用户信息失败', error)
        logout()
      }
    }
  }

  // 登录
  const login = async (username: string, password: string): Promise<{ success: boolean; dailyLoginReward?: boolean; coinsEarned?: number }> => {
    try {
      const res: LoginResponse = await userApi.login(username, password)
      token.value = res.access_token
      localStorage.setItem('token', res.access_token)
      user.value = res.user
      localStorage.setItem('user', JSON.stringify(res.user))

      // 显示每日登录奖励提示
      if (res.daily_login_reward && res.coins_earned > 0) {
        console.log(`登录成功！获得 ${res.coins_earned} 个硬币奖励`)
      } else {
        console.log('登录成功')
      }

      return { success: true, dailyLoginReward: res.daily_login_reward, coinsEarned: res.coins_earned }
    } catch (error) {
      console.error('登录失败', error)
      return { success: false }
    }
  }

  // 注册
  const register = async (username: string, email: string, password: string) => {
    try {
      await userApi.register(username, email, password)
      toast.success('注册成功，请登录')
      return true
    } catch (error) {
      console.error('注册失败', error)
      return false
    }
  }

  // 退出登录
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    toast.success('已退出登录')
  }

  // 更新用户硬币余额
  const updateCoins = (newBalance: number) => {
    if (user.value) {
      user.value.coins = newBalance
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  // 刷新用户信息
  const refreshUser = async () => {
    if (token.value) {
      try {
        const userData = await userApi.getMe()
        user.value = userData
        localStorage.setItem('user', JSON.stringify(userData))
      } catch (error) {
        console.error('刷新用户信息失败', error)
      }
    }
  }

  // 初始化
  initUser()

  return {
    user,
    token,
    login,
    register,
    logout,
    updateCoins,
    refreshUser,
    isAdmin: () => user.value?.role === 'admin',
    isLoggedIn: () => !!token.value
  }
})
