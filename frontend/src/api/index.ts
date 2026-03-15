import request from '@/utils/request'
import type { Video, Category, VideoListParams, VideoUploadForm, VideoInteraction, InteractionAction, LoginResponse, Audio, AudioListParams, AudioUploadForm, AudioInteraction, AudioInteractionAction } from '@/types'

// 视频相关 API
export const videoApi = {
  // 获取视频列表
  getVideos: (params: VideoListParams) => {
    return request.get<{ data: Video[] }>('/videos', { params })
  },

  // 获取视频详情
  getVideoDetail: (id: number) => {
    return request.get<Video>(`/videos/${id}`)
  },

  // 增加播放量
  incrementViews: (id: number) => {
    return request.post<{ views: number }>(`/videos/${id}/view`)
  },

  // 获取视频互动数据
  getInteractions: (id: number) => {
    return request.get<VideoInteraction>(`/videos/${id}/interactions`)
  },

  // 执行互动操作（点赞、投币、收藏、转发）
  doInteraction: (id: number, action: InteractionAction, count?: number) => {
    return request.post<VideoInteraction & { message: string }>(`/videos/${id}/interactions`, {
      action,
      count
    })
  },

  // 上传视频
  uploadVideo: async (form: VideoUploadForm) => {
    const formData = new FormData()
    formData.append('title', form.title)
    if (form.description) formData.append('description', form.description)
    if (form.category_id) formData.append('category_id', form.category_id.toString())
    if (form.visibility) formData.append('visibility', form.visibility)
    if (form.video_file) formData.append('video_file', form.video_file)
    if (form.cover_file) formData.append('cover_file', form.cover_file)

    return request.post<Video>('/admin/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 添加视频链接
  addVideoByURL: (form: VideoUploadForm) => {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('video_url', form.video_url || '')
    if (form.description) formData.append('description', form.description)
    if (form.category_id) formData.append('category_id', form.category_id.toString())
    if (form.visibility) formData.append('visibility', form.visibility)
    if (form.cover_url) formData.append('cover_url', form.cover_url)

    return request.post<Video>('/admin/videos/url', formData)
  },

  // 管理员获取视频列表
  adminGetVideos: (params: VideoListParams & { status?: string }) => {
    return request.get<Video[]>('/admin/videos', { params })
  },

  // 管理员获取视频详情
  adminGetVideoDetail: (id: number) => {
    return request.get<Video>(`/admin/videos/${id}`)
  },

  // 更新视频
  updateVideo: (id: number, form: Partial<VideoUploadForm>) => {
    return request.put<Video>(`/admin/videos/${id}`, form)
  },

  // 删除视频
  deleteVideo: (id: number) => {
    return request.delete<{ message: string }>(`/admin/videos/${id}`)
  }
}

// 用户视频管理 API
export const userVideoApi = {
  // 上传视频
  uploadVideo: async (form: VideoUploadForm) => {
    const formData = new FormData()
    formData.append('title', form.title)
    if (form.description) formData.append('description', form.description)
    if (form.category_id) formData.append('category_id', form.category_id.toString())
    if (form.visibility) formData.append('visibility', form.visibility)
    if (form.video_file) formData.append('video_file', form.video_file)
    if (form.cover_file) formData.append('cover_file', form.cover_file)

    return request.post<Video>('/user/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 添加视频链接
  addVideoByURL: (form: VideoUploadForm) => {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('video_url', form.video_url || '')
    if (form.description) formData.append('description', form.description)
    if (form.category_id) formData.append('category_id', form.category_id.toString())
    if (form.visibility) formData.append('visibility', form.visibility)
    if (form.cover_url) formData.append('cover_url', form.cover_url)

    return request.post<Video>('/user/videos/url', formData)
  },

  // 获取我的视频列表
  getMyVideos: (params: VideoListParams & { status?: string }) => {
    return request.get<Video[]>('/user/videos', { params })
  },

  // 获取视频详情
  getVideoDetail: (id: number) => {
    return request.get<Video>(`/user/videos/${id}`)
  },

  // 更新视频
  updateVideo: (id: number, form: Partial<VideoUploadForm>) => {
    return request.put<Video>(`/user/videos/${id}`, form)
  },

  // 删除视频
  deleteVideo: (id: number) => {
    return request.delete<{ message: string }>(`/user/videos/${id}`)
  }
}

// 分类相关 API
export const categoryApi = {
  // 获取分类列表
  getCategories: () => {
    return request.get<Category[]>('/videos/categories/list')
  }
}

// 用户相关 API
export const userApi = {
  // 用户登录
  login: (username: string, password: string) => {
    return request.post<LoginResponse>('/auth/login', new URLSearchParams({
      username,
      password
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },

  // 用户注册
  register: (username: string, email: string, password: string) => {
    return request.post('/auth/register', { username, email, password })
  },

  // 获取当前用户信息
  getMe: () => {
    return request.get('/auth/me')
  },

  // 更新用户信息
  updateMe: (data: { avatar?: string }) => {
    return request.put('/auth/me', data)
  }
}

// 音频相关 API
export const audioApi = {
  // 获取音频列表
  getAudios: (params: AudioListParams) => {
    return request.get<Audio[]>('/audios', { params })
  },

  // 获取音频详情
  getAudioDetail: (id: number) => {
    return request.get<Audio>(`/audios/${id}`)
  },

  // 增加播放量
  incrementPlays: (id: number) => {
    return request.post<{ plays: number }>(`/audios/${id}/play`)
  },

  // 获取音频互动数据
  getInteractions: (id: number) => {
    return request.get<AudioInteraction>(`/audios/${id}/interactions`)
  },

  // 执行互动操作（点赞、投币、收藏、转发）
  doInteraction: (id: number, action: AudioInteractionAction, count?: number) => {
    return request.post<AudioInteraction & { message: string }>(`/audios/${id}/interactions`, {
      action,
      count
    })
  }
}

// 用户音频管理 API
export const userAudioApi = {
  // 上传音频
  uploadAudio: async (form: AudioUploadForm) => {
    const formData = new FormData()
    formData.append('title', form.title)
    if (form.description) formData.append('description', form.description)
    if (form.category_id) formData.append('category_id', form.category_id.toString())
    if (form.visibility) formData.append('visibility', form.visibility)
    if (form.audio_file) formData.append('audio_file', form.audio_file)
    if (form.cover_file) formData.append('cover_file', form.cover_file)

    return request.post<Audio>('/user/audios/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 添加音频链接
  addAudioByURL: (form: AudioUploadForm) => {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('audio_url', form.audio_url || '')
    if (form.description) formData.append('description', form.description)
    if (form.category_id) formData.append('category_id', form.category_id.toString())
    if (form.visibility) formData.append('visibility', form.visibility)
    if (form.cover_url) formData.append('cover_url', form.cover_url)

    return request.post<Audio>('/user/audios/url', formData)
  },

  // 获取我的音频列表
  getMyAudios: (params: AudioListParams & { status?: string }) => {
    return request.get<Audio[]>('/user/audios', { params })
  },

  // 获取音频详情
  getAudioDetail: (id: number) => {
    return request.get<Audio>(`/user/audios/${id}`)
  },

  // 更新音频
  updateAudio: (id: number, form: Partial<AudioUploadForm>) => {
    return request.put<Audio>(`/user/audios/${id}`, form)
  },

  // 删除音频
  deleteAudio: (id: number) => {
    return request.delete<{ message: string }>(`/user/audios/${id}`)
  }
}
