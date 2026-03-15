// 视频相关类型
export interface Video {
  id: number
  title: string
  description?: string
  cover_url?: string
  video_url: string
  video_source: 'local' | 'url'
  category_id?: number
  category?: Category
  uploader_id: number
  uploader?: User
  duration: number
  views: number
  likes: number
  coins: number
  favorites: number
  shares: number
  visibility: 'public' | 'private'
  status: 'draft' | 'published' | 'archived'
  created_at: string
}

export interface Category {
  id: number
  name: string
  description?: string
  created_at: string
}

export interface User {
  id: number
  username: string
  email: string
  avatar?: string
  role: 'admin' | 'user'
  coins: number
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
  daily_login_reward: boolean
  coins_earned: number
}

export interface Comment {
  id: number
  video_id: number
  user: User
  content: string
  parent_id?: number
  created_at: string
}

export interface VideoListParams {
  page?: number
  page_size?: number
  category_id?: number
  search?: string
}

export interface VideoUploadForm {
  title: string
  description?: string
  category_id?: number
  video_url?: string
  visibility?: 'public' | 'private'
  cover_file?: File
  video_file?: File
}

export interface VideoInteraction {
  likes: number
  coins: number
  favorites: number
  shares: number
  user_liked: boolean
  user_coins: number
  user_favorited: boolean
  user_balance?: number
}

export type InteractionAction = 'like' | 'coin' | 'favorite' | 'share'

// 音频相关类型
export interface Audio {
  id: number
  title: string
  description?: string
  cover_url?: string
  audio_url: string
  audio_source: 'local' | 'url'
  category_id?: number
  category?: Category
  uploader_id: number
  uploader?: User
  duration: number
  plays: number
  likes: number
  coins: number
  favorites: number
  shares: number
  visibility: 'public' | 'private'
  status: 'draft' | 'published' | 'archived'
  created_at: string
}

export interface AudioListParams {
  page?: number
  page_size?: number
  category_id?: number
  search?: string
}

export interface AudioUploadForm {
  title: string
  description?: string
  category_id?: number
  audio_url?: string
  visibility?: 'public' | 'private'
  cover_file?: File
  audio_file?: File
  cover_url?: string
}

export interface AudioInteraction {
  likes: number
  coins: number
  favorites: number
  shares: number
  user_liked: boolean
  user_coins: number
  user_favorited: boolean
  user_balance?: number
}

export type AudioInteractionAction = 'like' | 'coin' | 'favorite' | 'share'
