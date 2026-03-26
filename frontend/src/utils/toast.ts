// Toast 工具 - 替代 Element Plus 的 ElMessage
type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastOptions {
  message: string
  type?: ToastType
  duration?: number
}

const getIcon = (type: ToastType): string => {
  switch (type) {
    case 'success':
      return '✓'
    case 'error':
      return '✕'
    case 'warning':
      return '⚠'
    case 'info':
      return 'ℹ'
    default:
      return ''
  }
}

const getColors = (type: ToastType): { bg: string; border: string } => {
  switch (type) {
    case 'success':
      return { bg: 'bg-green-50 dark:bg-green-900/30', border: 'border-green-500' }
    case 'error':
      return { bg: 'bg-red-50 dark:bg-red-900/30', border: 'border-red-500' }
    case 'warning':
      return { bg: 'bg-yellow-50 dark:bg-yellow-900/30', border: 'border-yellow-500' }
    case 'info':
      return { bg: 'bg-blue-50 dark:bg-blue-900/30', border: 'border-blue-500' }
    default:
      return { bg: 'bg-gray-50 dark:bg-gray-800', border: 'border-gray-500' }
  }
}

const getTextColor = (type: ToastType): string => {
  switch (type) {
    case 'success':
      return 'text-green-700 dark:text-green-300'
    case 'error':
      return 'text-red-700 dark:text-red-300'
    case 'warning':
      return 'text-yellow-700 dark:text-yellow-300'
    case 'info':
      return 'text-blue-700 dark:text-blue-300'
    default:
      return 'text-gray-700 dark:text-gray-300'
  }
}

export const toast = {
  show(options: ToastOptions): void {
    const { message, type = 'info', duration = 3000 } = options

    // 创建容器
    let container = document.getElementById('toast-container')
    if (!container) {
      container = document.createElement('div')
      container.id = 'toast-container'
      container.className = 'fixed top-4 right-4 z-[9999] flex flex-col gap-2'
      document.body.appendChild(container)
    }

    // 创建 toast 元素
    const toastEl = document.createElement('div')
    const colors = getColors(type)
    const textColor = getTextColor(type)

    toastEl.className = `
      flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg
      border-l-4 ${colors.bg} ${colors.border}
      ${textColor}
      transform translate-x-full opacity-0
      transition-all duration-300 ease-out
      max-w-sm
    `.trim().replace(/\s+/g, ' ')

    toastEl.innerHTML = `
      <span class="text-lg">${getIcon(type)}</span>
      <span class="text-sm font-medium">${message}</span>
    `

    container.appendChild(toastEl)

    // 触发动画
    requestAnimationFrame(() => {
      toastEl.classList.remove('translate-x-full', 'opacity-0')
    })

    // 自动移除
    setTimeout(() => {
      toastEl.classList.add('translate-x-full', 'opacity-0')
      setTimeout(() => {
        toastEl.remove()
        // 如果容器为空，移除容器
        if (container && container.children.length === 0) {
          container.remove()
        }
      }, 300)
    }, duration)
  },

  success(message: string, duration?: number): void {
    this.show({ message, type: 'success', duration })
  },

  error(message: string, duration?: number): void {
    this.show({ message, type: 'error', duration })
  },

  warning(message: string, duration?: number): void {
    this.show({ message, type: 'warning', duration })
  },

  info(message: string, duration?: number): void {
    this.show({ message, type: 'info', duration })
  }
}

export default toast