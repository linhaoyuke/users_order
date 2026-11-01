import request from '@/utils/request'
import type {Permission} from '@/types/auth'

export interface CreatePermissionForm {
  name: string
  code: string
  description?: string
  resource: string
  action: string
}

export interface UpdatePermissionForm {
  name?: string
  code?: string
  description?: string
  resource?: string
  action?: string
}

export const permissionApi = {
  // 获取权限列表
  getPermissions: () => {
    return request.get<Permission[]>('/permissions/')
  },

  // 创建权限
  createPermission: (data: CreatePermissionForm) => {
    return request.post<Permission>('/permissions/', data)
  },

  // 更新权限
  updatePermission: (id: number, data: UpdatePermissionForm) => {
    return request.put<Permission>(`/permissions/${id}`, data)
  },

  // 删除权限
  deletePermission: (id: number) => {
    return request.delete(`/permissions/${id}`)
  }
}
