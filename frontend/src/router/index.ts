import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/videos',
    name: 'Videos',
    component: () => import('@/views/Videos.vue'),
    meta: { title: '视频列表' }
  },
  {
    path: '/audios',
    name: 'Audios',
    component: () => import('@/views/Audios.vue'),
    meta: { title: '音频列表' }
  },
  {
    path: '/video/:id',
    name: 'Video',
    component: () => import('@/views/VideoDetail.vue'),
    meta: { title: '视频详情' }
  },
  {
    path: '/audio/:id',
    name: 'Audio',
    component: () => import('@/views/AudioDetail.vue'),
    meta: { title: '音频详情' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin/Index.vue'),
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/videos'
      },
      {
        path: 'videos',
        name: 'AdminVideos',
        component: () => import('@/views/admin/Videos.vue'),
        meta: { title: '视频管理' }
      },
      {
        path: 'upload',
        name: 'AdminUpload',
        component: () => import('@/views/admin/Upload.vue'),
        meta: { title: '上传视频' }
      }
    ]
  },
  // 用户投稿管理
  {
    path: '/studio',
    name: 'Studio',
    component: () => import('@/views/studio/Index.vue'),
    meta: { title: '创作中心', requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/studio/videos'
      },
      {
        path: 'videos',
        name: 'StudioVideos',
        component: () => import('@/views/studio/Videos.vue'),
        meta: { title: '稿件管理' }
      },
      {
        path: 'upload',
        name: 'StudioUpload',
        component: () => import('@/views/studio/Upload.vue'),
        meta: { title: '上传视频' }
      },
      {
        path: 'audios',
        name: 'StudioAudios',
        component: () => import('@/views/studio/Audios.vue'),
        meta: { title: '音频管理' }
      },
      {
        path: 'upload-audio',
        name: 'StudioUploadAudio',
        component: () => import('@/views/studio/UploadAudio.vue'),
        meta: { title: '上传音频' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '视频平台'} - 视频平台`

  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  // 检查是否需要登录
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && user.role !== 'admin') {
    next('/')
    return
  }

  next()
})

export default router
