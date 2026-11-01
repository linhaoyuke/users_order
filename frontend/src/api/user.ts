import request from '@/utils/request'
import type {CreateUserForm, UpdateUserForm, User} from '@/types/user'

export const userApi = {
  // 获取用户列表（支持搜索和分页）
  getUsers: (params?: { search?: string; page?: number; page_size?: number }) => {
    return request.get<{ count: number; results: User[] }>('/users/', { params })
  },

  // 获取所有用户，用于下拉选择框
  getAllUsers: () => {
    return request.get<User[]>('/users/all')
  },

  // 创建用户
  createUser: (data: CreateUserForm) => {
    return request.post<User>('/users/', data)
  },

  // 更新用户
  updateUser: (id: number, data: UpdateUserForm) => {
    return request.put<User>(`/users/${id}`, data)
  },

  // 删除用户
  deleteUser: (id: number) => {
    return request.delete(`/users/${id}`)
  },

  // 分配角色
  assignRoles: (userId: number, roleIds: number[]) => {
    return request.post(`/users/${userId}/roles`, { role_ids: roleIds })
  },

  

  // 获取当前用户信息
  getCurrentUserProfile: () => {
    return request.get<User>('/users/profile')
  },

  // 更新当前用户信息
  updateCurrentUserProfile: (data: Partial<User>) => {
    return request.put<User>('/users/profile', data)
  },

  // 修改当前用户密码
  changePassword: (data: { old_password: string; new_password: string }) => {
    return request.post('/users/change-password', data)
  },

  // 修改当前用户邮箱
  changeEmail: (data: { new_email: string }) => {
    return request.post<User>('/users/change-email', data)
  },

  // 修改当前用户手机号
  changePhone: (data: { new_phone: string }) => {
    return request.post<User>('/users/change-phone', data)
  }
}
