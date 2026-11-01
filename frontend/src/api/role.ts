import request from '@/utils/request'
import type {Role} from '@/types/auth'

export interface CreateRoleForm {
  name: string
  code: string
  description?: string
  permission_ids?: number[]
}

export interface UpdateRoleForm {
  name?: string
  code?: string
  description?: string
  permission_ids?: number[]
}

export const roleApi = {
  // 获取角色列表
  getRoles: () => {
    return request.get<Role[]>('/roles/')
  },

  // 创建角色
  createRole: (data: CreateRoleForm) => {
    return request.post<Role>('/roles/', data)
  },

  // 更新角色
  updateRole: (id: number, data: UpdateRoleForm) => {
    return request.put<Role>(`/roles/${id}`, data)
  },

  // 删除角色
  deleteRole: (id: number) => {
    return request.delete(`/roles/${id}`)
  },

  // 分配权限
  assignPermissions: (roleId: number, permissionIds: number[]) => {
    return request.post(`/roles/${roleId}/permissions`, { permission_ids: permissionIds })
  }
}
