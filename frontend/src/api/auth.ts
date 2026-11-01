import request from '@/utils/request'
import type {LoginForm, LoginResponse} from '@/types/auth'

export const authApi = {
  // 获取验证码
  getCaptcha: () => {
    return request.get<{ image: string, token: string }>('/auth/captcha')
  },

  // 登录
  login: (data: LoginForm) => {
    return request.post<LoginResponse>('/auth/login', data)
  },

  // 刷新token
  refresh: (refreshToken: string) => {
    return request.post('/auth/refresh', {}, {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    })
  },

  // 退出登录
  logout: () => {
    return request.post('/auth/logout')
  }
}

// 导出单独的函数以便使用
export const getCaptcha = authApi.getCaptcha
