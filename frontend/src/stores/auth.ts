import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import {jwtDecode} from 'jwt-decode'
import type {JwtPayload, LoginForm, User} from '@/types/auth'
import {authApi} from '@/api/auth'
import {ElMessage} from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  // 1. 状态定义：从 localStorage 初始化
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))
  const permissions = ref<string[]>(JSON.parse(localStorage.getItem('permissions') || '[]'))
  const loading = ref(false)

  // 2. 计算属性：认证状态的唯一信源
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 3. 核心方法：设置和清除会话
  const setSession = (accessToken: string, newRefreshToken: string, userInfo: User) => {
    token.value = accessToken
    refreshToken.value = newRefreshToken
    user.value = userInfo

    localStorage.setItem('token', accessToken)
    localStorage.setItem('refreshToken', newRefreshToken)
    localStorage.setItem('user', JSON.stringify(userInfo))

    // 解码并存储权限
    try {
      const decoded = jwtDecode<JwtPayload>(accessToken)
      permissions.value = decoded.permissions || []
      localStorage.setItem('permissions', JSON.stringify(permissions.value))
    } catch (error) {
      console.error('解码Token失败:', error)
      permissions.value = []
      localStorage.removeItem('permissions')
    }
  }

  const clearSession = () => {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    permissions.value = []

    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    localStorage.removeItem('permissions')
  }

  // 4. 用户操作
  const login = async (loginForm: LoginForm) => {
    loading.value = true
    try {
      const response = await authApi.login(loginForm)
      const { access_token, refresh_token, user: userInfo } = response.data
      setSession(access_token, refresh_token, userInfo)
      ElMessage.success('登录成功')
      return true
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '登录失败')
      clearSession() // 登录失败也清除一下，防止状态不一致
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async (skipApiCall = false) => {
    try {
      if (token.value && !skipApiCall) {
        await authApi.logout()
      }
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      clearSession()
      if (!skipApiCall) {
        ElMessage.success('已退出登录')
      }
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }
    try {
      const response = await authApi.refresh(refreshToken.value)
      const { access_token } = response.data
      token.value = access_token
      localStorage.setItem('token', access_token)
      
      // 刷新token后，user信息不变，但需要重新解析权限
      try {
        const decoded = jwtDecode<JwtPayload>(access_token)
        permissions.value = decoded.permissions || []
        localStorage.setItem('permissions', JSON.stringify(permissions.value))
      } catch (error) {
        permissions.value = []
        localStorage.removeItem('permissions')
      }

      return access_token
    } catch (error) {
      logout(true) // 刷新失败，强制登出
      throw error
    }
  }

  // 5. 权限检查
  const hasPermission = (permission: string) => {
    // 超级管理员角色默认具备所有权限
    if (hasRole('admin')) return true
    // 权限来源是后端JWT解码出的permissions列表
    return permissions.value.includes(permission)
  }

  const hasAnyPermission = (permList: string[]) => {
    if (hasRole('admin')) return true
    return permList.some(perm => permissions.value.includes(perm))
  }

  const hasRole = (roleCode: string) => {
    if (!user.value || !user.value.roles) return false
    return user.value.roles.some(role => role.code === roleCode)
  }

  return {
    token,
    refreshToken,
    user,
    permissions,
    loading,
    isAuthenticated,
    login,
    logout,
    refreshAccessToken,
    hasPermission,
    hasAnyPermission,
    hasRole
  }
})
