import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()

    // 添加token到请求头
    if (authStore.token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 防止重复刷新token的标志
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: any) => void
  reject: (reason?: any) => void
}> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })

  failedQueue = []
}

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const authStore = useAuthStore()
    const originalRequest = error.config

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // 如果是刷新token的请求失败，直接退出登录
          if (originalRequest.url?.includes('/auth/refresh')) {
            ElMessage.error('登录已过期，请重新登录')
            authStore.logout(true) // 跳过API调用
            router.push('/login')
            return Promise.reject(error)
          }

          // token过期或无效，且有refresh token
          if (authStore.refreshToken && !originalRequest._retry) {
            if (isRefreshing) {
              // 如果正在刷新，将请求加入队列
              return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject })
              }).then(token => {
                originalRequest.headers.Authorization = `Bearer ${token}`
                return service.request(originalRequest)
              }).catch(err => {
                return Promise.reject(err)
              })
            }

            originalRequest._retry = true
            isRefreshing = true

            try {
              // 尝试刷新token
              const newToken = await authStore.refreshAccessToken()
              processQueue(null, newToken)
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              return service.request(originalRequest)
            } catch (refreshError) {
              // 刷新失败，清空队列并跳转到登录页
              processQueue(refreshError, null)
              ElMessage.error('登录已过期，请重新登录')
              authStore.logout(true) // 跳过API调用
              router.push('/login')
              return Promise.reject(refreshError)
            } finally {
              isRefreshing = false
            }
          } else {
            ElMessage.error('请先登录')
            authStore.logout(true) // 跳过API调用
            router.push('/login')
          }
          break

        case 422:
          // JWT格式错误，强制重新登录
          ElMessage.error('Token格式错误，请重新登录')
          authStore.logout(true) // 跳过API调用
          router.push('/login')
          break

        case 403:
          ElMessage.error('没有权限访问该资源')
          break

        case 404:
          ElMessage.error('请求的资源不存在')
          break

        case 500:
          ElMessage.error('服务器内部错误')
          break

        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default service
